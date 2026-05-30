"""Typer CLI for Petstore gRPC and REST endpoints."""

from __future__ import annotations

import json
import logging
import random
import string
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import grpc
import typer
from google.protobuf.json_format import MessageToDict

from petstore_grpc.generated.petstore.v1 import (
    common_pb2,
    health_pb2,
    health_pb2_grpc,
    pet_pb2,
    pet_pb2_grpc,
)

app = typer.Typer(help="Petstore CLI with env + transport defaults.", no_args_is_help=True)
pet_app = typer.Typer(help="Pet operations.")
app.add_typer(pet_app, name="pet")


class Environment(StrEnum):
    """Supported target environments."""

    LOCAL = "local"
    DEV = "dev"
    STAGING = "staging"


class Transport(StrEnum):
    """Supported transports."""

    GRPC = "grpc"
    REST = "rest"


@dataclass(frozen=True)
class EnvTargets:
    """Endpoint targets for one environment."""

    grpc_target: str
    rest_base_url: str
    grpc_tls: bool


@dataclass(frozen=True)
class AppContext:
    """Resolved runtime context."""

    env: Environment
    transport: Transport
    grpc_target: str
    rest_base_url: str
    log_file: Path
    logger: logging.Logger
    request_timeout: float
    max_retries: int
    retry_backoff_seconds: float


_DEFAULT_TARGETS: dict[Environment, EnvTargets] = {
    Environment.LOCAL: EnvTargets(
        grpc_target="localhost:50051",
        rest_base_url="http://localhost:8080",
        grpc_tls=False,
    ),
    Environment.DEV: EnvTargets(
        grpc_target="petstore-grpc-dev.fly.dev:443",
        rest_base_url="https://petstore-grpc-dev.fly.dev",
        grpc_tls=True,
    ),
    Environment.STAGING: EnvTargets(
        grpc_target="petstore-grpc-staging.fly.dev:443",
        rest_base_url="https://petstore-grpc-staging.fly.dev",
        grpc_tls=True,
    ),
}

_STATUS_TO_ENUM: dict[str, int] = {
    "available": common_pb2.PET_STATUS_AVAILABLE,
    "pending": common_pb2.PET_STATUS_PENDING,
    "sold": common_pb2.PET_STATUS_SOLD,
}


def _setup_logger(log_file: Path) -> logging.Logger:
    """Create file logger for request/response logging."""
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("petstore_cli")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(file_handler)
    return logger


def _log_event(ctx: AppContext, phase: str, operation: str, payload: dict[str, Any]) -> None:
    """Write a structured request/response event."""
    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "environment": ctx.env.value,
        "transport": ctx.transport.value,
        "phase": phase,
        "operation": operation,
        "payload": payload,
    }
    ctx.logger.info(json.dumps(entry, separators=(",", ":"), default=str))


def _pretty_print(data: dict[str, Any]) -> None:
    """Print JSON in human-readable form."""
    typer.echo(json.dumps(data, indent=2, sort_keys=True))


def _proto_to_dict(message: Any) -> dict[str, Any]:
    """Convert protobuf message to plain dict."""
    return MessageToDict(message, preserving_proto_field_name=False)


def _fail(message: str) -> None:
    """Print error and stop execution."""
    typer.secho(message, fg=typer.colors.RED)
    raise typer.Exit(code=1)


def _resolve_status(value: str) -> int:
    """Resolve status string into proto enum value."""
    enum_value = _STATUS_TO_ENUM.get(value.lower())
    if enum_value is None:
        _fail("Invalid status. Allowed values: available, pending, sold.")
    return enum_value


def _build_sample_pet(
    name: str | None,
    status: str,
    photo_url: str | None,
    category: str | None,
    tag: str | None,
) -> dict[str, Any]:
    """Build a sensible default pet payload."""
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    resolved_name = name or f"pet-{suffix}"
    resolved_photo = photo_url or f"https://picsum.photos/seed/{suffix}/640/480"
    resolved_category = category or "generated"
    resolved_tag = tag or "autogen"
    return {
        "name": resolved_name,
        "status": status.lower(),
        "photo_urls": [resolved_photo],
        "category": {"name": resolved_category},
        "tags": [{"name": resolved_tag}],
    }


@contextmanager
def _grpc_channel(ctx: AppContext):
    """Open a gRPC channel for the selected environment."""
    if _DEFAULT_TARGETS[ctx.env].grpc_tls:
        channel = grpc.secure_channel(ctx.grpc_target, grpc.ssl_channel_credentials())
    else:
        channel = grpc.insecure_channel(ctx.grpc_target)
    try:
        yield channel
    finally:
        channel.close()


def _grpc_call(ctx: AppContext, operation: str, request: Any, rpc: Any) -> dict[str, Any]:
    """Execute a unary gRPC request and return decoded response."""
    request_payload = _proto_to_dict(request)
    _log_event(
        ctx,
        phase="request",
        operation=operation,
        payload={"target": ctx.grpc_target, "request": request_payload},
    )
    response = None
    for attempt in range(ctx.max_retries + 1):
        try:
            response = rpc(request, timeout=ctx.request_timeout)
            break
        except grpc.RpcError as exc:
            details = {"code": exc.code().name, "details": exc.details()}
            can_retry = exc.code() is grpc.StatusCode.UNAVAILABLE and attempt < ctx.max_retries
            if can_retry:
                retry_in_seconds = min(ctx.retry_backoff_seconds * (2**attempt), 10.0)
                _log_event(
                    ctx,
                    phase="response",
                    operation=operation,
                    payload={
                        **details,
                        "attempt": attempt + 1,
                        "max_attempts": ctx.max_retries + 1,
                        "retry_in_seconds": retry_in_seconds,
                    },
                )
                time.sleep(retry_in_seconds)
                continue
            _log_event(ctx, phase="response", operation=operation, payload=details)
            _fail(f"gRPC call failed: {details['code']} - {details['details']}")
            raise  # Unreachable, but keeps type-checkers happy.

    if response is None:
        _fail("gRPC call failed: exhausted retries.")
        raise RuntimeError("unreachable")

    response_payload = _proto_to_dict(response)
    _log_event(
        ctx,
        phase="response",
        operation=operation,
        payload={"target": ctx.grpc_target, "response": response_payload},
    )
    return response_payload


def _grpc_http_unary_call(
    ctx: AppContext,
    operation: str,
    method_path: str,
    request_message: Any,
    response_type: Any,
) -> dict[str, Any]:
    """Call unary gRPC method over raw HTTP framing through the REST base URL."""
    url = f"{ctx.rest_base_url.rstrip('/')}{method_path}"
    message_bytes = request_message.SerializeToString()
    body = b"\x00" + len(message_bytes).to_bytes(4, byteorder="big") + message_bytes
    headers = {
        "content-type": "application/grpc",
        "te": "trailers",
    }
    _log_event(
        ctx,
        phase="request",
        operation=operation,
        payload={"method": "POST", "url": url, "request": _proto_to_dict(request_message)},
    )
    request = Request(url, data=body, headers=headers, method="POST")
    try:
        with urlopen(request, timeout=30) as response:
            response_body = response.read()
            status_code = response.getcode()
            grpc_status = response.headers.get("grpc-status", "")
            grpc_message = response.headers.get("grpc-message", "")
    except HTTPError as exc:
        response_body = exc.read()
        status_code = exc.code
        grpc_status = exc.headers.get("grpc-status", "")
        grpc_message = exc.headers.get("grpc-message", "")
    except URLError as exc:
        _log_event(
            ctx,
            phase="response",
            operation=operation,
            payload={"url": url, "error": str(exc.reason)},
        )
        _fail(f"REST call failed: {exc.reason}")

    response_payload: dict[str, Any] = {}
    metadata: dict[str, Any] = {
        "http_status": status_code,
        "grpc_status": grpc_status,
        "grpc_message": grpc_message,
    }
    if metadata["grpc_status"] == "" and status_code == 200:
        metadata["grpc_status"] = "0"

    if len(response_body) >= 5 and response_body[0] == 0:
        try:
            message_size = int.from_bytes(response_body[1:5], byteorder="big")
            message_body = response_body[5 : 5 + message_size]
            decoded = response_type.FromString(message_body)
            response_payload = _proto_to_dict(decoded)
        except Exception as exc:
            metadata["decode_error"] = str(exc)
            metadata["raw_hex"] = response_body.hex()
    elif response_body:
        metadata["raw_hex"] = response_body.hex()

    _log_event(
        ctx,
        phase="response",
        operation=operation,
        payload={"metadata": metadata, "response": response_payload},
    )
    if metadata["grpc_status"] != "0":
        _fail(f"REST gRPC call failed: {metadata['grpc_status']} - {metadata['grpc_message']}")
    return response_payload


def _ctx(typer_ctx: typer.Context) -> AppContext:
    """Return typed app context."""
    return typer_ctx.obj


@app.callback()
def main(
    ctx: typer.Context,
    env: Annotated[Environment, typer.Option(help="Target environment.")] = Environment.DEV,
    transport: Annotated[Transport, typer.Option(help="Transport: grpc or rest.")] = (
        Transport.GRPC
    ),
    grpc_target: Annotated[str | None, typer.Option(help="Override gRPC host:port.")] = None,
    rest_base_url: Annotated[str | None, typer.Option(help="Override REST base URL.")] = None,
    log_file: Annotated[
        Path,
        typer.Option(help="Log file path for request/response events."),
    ] = Path("cli/logs/petstore_cli.log"),
    request_timeout: Annotated[
        float,
        typer.Option(help="Per-request timeout in seconds."),
    ] = 60.0,
    max_retries: Annotated[
        int,
        typer.Option(help="Retries for transient gRPC UNAVAILABLE errors."),
    ] = 5,
    retry_backoff_seconds: Annotated[
        float,
        typer.Option(help="Base backoff seconds for gRPC retry delays."),
    ] = 1.0,
) -> None:
    """Initialize CLI context with defaults for env + transport."""
    if request_timeout <= 0:
        raise typer.BadParameter("--request-timeout must be greater than 0.")
    if max_retries < 0:
        raise typer.BadParameter("--max-retries must be 0 or greater.")
    if retry_backoff_seconds <= 0:
        raise typer.BadParameter("--retry-backoff-seconds must be greater than 0.")

    defaults = _DEFAULT_TARGETS[env]
    logger = _setup_logger(log_file)
    ctx.obj = AppContext(
        env=env,
        transport=transport,
        grpc_target=grpc_target or defaults.grpc_target,
        rest_base_url=rest_base_url or defaults.rest_base_url,
        log_file=log_file,
        logger=logger,
        request_timeout=request_timeout,
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff_seconds,
    )


@app.command("config")
def show_config(ctx: typer.Context) -> None:
    """Print resolved target config."""
    app_ctx = _ctx(ctx)
    _pretty_print(
        {
            "environment": app_ctx.env.value,
            "transport": app_ctx.transport.value,
            "grpc_target": app_ctx.grpc_target,
            "rest_base_url": app_ctx.rest_base_url,
            "log_file": str(app_ctx.log_file),
            "request_timeout": app_ctx.request_timeout,
            "max_retries": app_ctx.max_retries,
            "retry_backoff_seconds": app_ctx.retry_backoff_seconds,
        }
    )


@app.command("health")
def health_check(ctx: typer.Context) -> None:
    """Call health endpoint for active transport."""
    app_ctx = _ctx(ctx)
    if app_ctx.transport is Transport.GRPC:
        with _grpc_channel(app_ctx) as channel:
            stub = health_pb2_grpc.HealthStub(channel)
            request = health_pb2.HealthRequest()
            result = _grpc_call(app_ctx, "health.check", request, stub.Check)
    else:
        result = _grpc_http_unary_call(
            app_ctx,
            "health.check",
            "/petstore.v1.Health/Check",
            health_pb2.HealthRequest(),
            health_pb2.HealthResponse,
        )
    _pretty_print(result)


@pet_app.command("add")
def add_pet(
    ctx: typer.Context,
    name: Annotated[str | None, typer.Option(help="Pet name. Defaults to generated value.")] = None,
    status: Annotated[str, typer.Option(help="Pet status: available|pending|sold.")] = "available",
    photo_url: Annotated[
        str | None,
        typer.Option(help="Photo URL. Defaults to generated value."),
    ] = None,
    category: Annotated[str | None, typer.Option(help="Category name.")] = None,
    tag: Annotated[str | None, typer.Option(help="Tag name.")] = None,
) -> None:
    """Add pet with sensible defaults when args are omitted."""
    app_ctx = _ctx(ctx)
    sample_pet = _build_sample_pet(name, status, photo_url, category, tag)
    request = pet_pb2.AddPetRequest(
        pet=common_pb2.Pet(
            name=sample_pet["name"],
            photo_urls=sample_pet["photo_urls"],
            category=common_pb2.Category(name=sample_pet["category"]["name"]),
            tags=[common_pb2.Tag(name=sample_pet["tags"][0]["name"])],
            status=_resolve_status(sample_pet["status"]),
        )
    )

    if app_ctx.transport is Transport.GRPC:
        with _grpc_channel(app_ctx) as channel:
            stub = pet_pb2_grpc.PetServiceStub(channel)
            result = _grpc_call(app_ctx, "pet.add", request, stub.AddPet)
    else:
        result = _grpc_http_unary_call(
            app_ctx,
            "pet.add",
            "/petstore.v1.PetService/AddPet",
            request,
            common_pb2.Pet,
        )

    _pretty_print(result)


@pet_app.command("get")
def get_pet(
    ctx: typer.Context,
    pet_id: Annotated[int, typer.Argument(help="Pet ID.")],
) -> None:
    """Get pet by ID."""
    app_ctx = _ctx(ctx)
    request = pet_pb2.GetPetByIdRequest(pet_id=pet_id)
    if app_ctx.transport is Transport.GRPC:
        with _grpc_channel(app_ctx) as channel:
            stub = pet_pb2_grpc.PetServiceStub(channel)
            result = _grpc_call(app_ctx, "pet.get", request, stub.GetPetById)
    else:
        result = _grpc_http_unary_call(
            app_ctx,
            "pet.get",
            "/petstore.v1.PetService/GetPetById",
            request,
            common_pb2.Pet,
        )
    _pretty_print(result)


@pet_app.command("list")
def list_pets(
    ctx: typer.Context,
    status: Annotated[
        str | None,
        typer.Option(help="Status filter: available|pending|sold. Defaults to all for gRPC."),
    ] = None,
    skip: Annotated[int, typer.Option(help="Records to skip.")] = 0,
    limit: Annotated[int, typer.Option(help="Max number of records.")] = 20,
) -> None:
    """List pets."""
    app_ctx = _ctx(ctx)
    request = pet_pb2.FindPetsByStatusRequest(skip=skip, limit=limit)
    if status:
        request.status = _resolve_status(status)
    if app_ctx.transport is Transport.GRPC:
        with _grpc_channel(app_ctx) as channel:
            stub = pet_pb2_grpc.PetServiceStub(channel)
            result = _grpc_call(app_ctx, "pet.list", request, stub.FindPetsByStatus)
    else:
        result = _grpc_http_unary_call(
            app_ctx,
            "pet.list",
            "/petstore.v1.PetService/FindPetsByStatus",
            request,
            pet_pb2.FindPetsByStatusResponse,
        )
    _pretty_print(result)


@pet_app.command("delete")
def delete_pet(
    ctx: typer.Context,
    pet_id: Annotated[int, typer.Argument(help="Pet ID.")],
) -> None:
    """Delete pet by ID."""
    app_ctx = _ctx(ctx)
    request = pet_pb2.DeletePetRequest(pet_id=pet_id)
    if app_ctx.transport is Transport.GRPC:
        with _grpc_channel(app_ctx) as channel:
            stub = pet_pb2_grpc.PetServiceStub(channel)
            result = _grpc_call(app_ctx, "pet.delete", request, stub.DeletePet)
    else:
        result = _grpc_http_unary_call(
            app_ctx,
            "pet.delete",
            "/petstore.v1.PetService/DeletePet",
            request,
            pet_pb2.DeletePetResponse,
        )
    _pretty_print(result)


def run() -> None:
    """Run the CLI application."""
    app()


if __name__ == "__main__":
    run()
