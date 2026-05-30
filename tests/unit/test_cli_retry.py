"""Unit tests for CLI gRPC retry behavior."""

from __future__ import annotations

import json
from pathlib import Path

import grpc
import pytest
import typer
from cli.main import AppContext, Environment, Transport, _grpc_call, _setup_logger

from petstore_grpc.generated.petstore.v1 import health_pb2


class FakeRpcError(grpc.RpcError):
    """Minimal RpcError for deterministic retry testing."""

    def __init__(self, status_code: grpc.StatusCode, message: str) -> None:
        super().__init__()
        self._status_code = status_code
        self._message = message

    def code(self) -> grpc.StatusCode:
        return self._status_code

    def details(self) -> str:
        return self._message


def _ctx(log_file: Path, *, max_retries: int = 2, backoff: float = 0.1) -> AppContext:
    """Build AppContext for retry tests."""
    return AppContext(
        env=Environment.DEV,
        transport=Transport.GRPC,
        grpc_target="example.org:443",
        rest_base_url="https://example.org",
        log_file=log_file,
        logger=_setup_logger(log_file),
        request_timeout=60.0,
        max_retries=max_retries,
        retry_backoff_seconds=backoff,
    )


def test_grpc_call_retries_unavailable_and_logs_attempts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """UNAVAILABLE errors should be retried and annotated in logs."""
    monkeypatch.setattr("cli.main.time.sleep", lambda _: None)
    log_file = tmp_path / "cli.log"
    ctx = _ctx(log_file, max_retries=2, backoff=0.1)
    request = health_pb2.HealthRequest()

    attempts = {"count": 0}

    def rpc(_: health_pb2.HealthRequest, timeout: float) -> health_pb2.HealthResponse:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise FakeRpcError(grpc.StatusCode.UNAVAILABLE, "Connection refused")
        return health_pb2.HealthResponse(status="SERVING")

    result = _grpc_call(ctx, "health.check", request, rpc)

    assert attempts["count"] == 3
    assert result["status"] == "SERVING"

    lines = [json.loads(line) for line in log_file.read_text().splitlines()]
    retry_entries = [
        line
        for line in lines
        if line["phase"] == "response" and line["payload"].get("code") == "UNAVAILABLE"
    ]
    assert len(retry_entries) == 2
    assert retry_entries[0]["payload"]["attempt"] == 1
    assert retry_entries[1]["payload"]["attempt"] == 2
    assert retry_entries[0]["payload"]["max_attempts"] == 3
    assert retry_entries[1]["payload"]["max_attempts"] == 3


def test_grpc_call_logs_final_failed_attempt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Final failed attempt should also include attempt metadata in logs."""
    monkeypatch.setattr("cli.main.time.sleep", lambda _: None)
    log_file = tmp_path / "cli.log"
    ctx = _ctx(log_file, max_retries=2, backoff=0.1)
    request = health_pb2.HealthRequest()

    def rpc(_: health_pb2.HealthRequest, timeout: float) -> health_pb2.HealthResponse:
        raise FakeRpcError(grpc.StatusCode.UNAVAILABLE, "Connection refused")

    with pytest.raises(typer.Exit):
        _grpc_call(ctx, "health.check", request, rpc)

    lines = [json.loads(line) for line in log_file.read_text().splitlines()]
    failed_entries = [
        line
        for line in lines
        if line["phase"] == "response" and line["payload"].get("code") == "UNAVAILABLE"
    ]
    assert len(failed_entries) == 3
    assert failed_entries[0]["payload"]["attempt"] == 1
    assert failed_entries[1]["payload"]["attempt"] == 2
    assert failed_entries[2]["payload"]["attempt"] == 3
    assert all(entry["payload"]["max_attempts"] == 3 for entry in failed_entries)


def test_grpc_call_does_not_retry_non_unavailable(tmp_path: Path) -> None:
    """Non-UNAVAILABLE errors should fail immediately without retries."""
    log_file = tmp_path / "cli.log"
    ctx = _ctx(log_file, max_retries=5, backoff=0.1)
    request = health_pb2.HealthRequest()

    attempts = {"count": 0}

    def rpc(_: health_pb2.HealthRequest, timeout: float) -> health_pb2.HealthResponse:
        attempts["count"] += 1
        raise FakeRpcError(grpc.StatusCode.INVALID_ARGUMENT, "invalid")

    with pytest.raises(typer.Exit):
        _grpc_call(ctx, "health.check", request, rpc)

    assert attempts["count"] == 1
