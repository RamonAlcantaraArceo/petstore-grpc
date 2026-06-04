"""Client abstractions for system/e2e transport tests."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import grpc
from google.protobuf.message import Message

from petstore_grpc.generated.petstore.v1 import (
    common_pb2,
    health_pb2,
    health_pb2_grpc,
    pet_pb2,
    pet_pb2_grpc,
)


@dataclass(frozen=True)
class ClientTargets:
    """Network targets for each transport."""

    grpc_target: str
    envoy_base_url: str


class BasePetstoreClient:
    """Unified client interface for transport parity tests."""

    transport_name: str

    def health_check(self) -> health_pb2.HealthResponse:
        """Run health check for this transport."""
        raise NotImplementedError

    def list_available_pets(self, limit: int = 10) -> pet_pb2.FindPetsByStatusResponse:
        """List available pets for this transport."""
        raise NotImplementedError

    def get_pet(self, pet_id: int) -> pet_pb2.GetPetByIdResponse:
        """Fetch one pet by id for this transport."""
        raise NotImplementedError

    def close(self) -> None:
        """Release transport resources."""


class GrpcPetstoreClient(BasePetstoreClient):
    """Native gRPC transport client."""

    transport_name = "grpc"

    def __init__(self, target: str) -> None:
        """Create gRPC client bound to target host:port."""
        self._channel = grpc.insecure_channel(target)
        self._health = health_pb2_grpc.HealthStub(self._channel)
        self._pet = pet_pb2_grpc.PetServiceStub(self._channel)

    def health_check(self) -> health_pb2.HealthResponse:
        """Run health check via native gRPC."""
        return self._health.Check(health_pb2.HealthRequest(), timeout=10)

    def list_available_pets(self, limit: int = 10) -> pet_pb2.FindPetsByStatusResponse:
        """List pets with available status."""
        return self._pet.FindPetsByStatus(
            pet_pb2.FindPetsByStatusRequest(status=common_pb2.PET_STATUS_AVAILABLE, limit=limit),
            timeout=10,
        )

    def get_pet(self, pet_id: int) -> pet_pb2.GetPetByIdResponse:
        """Fetch one pet by id."""
        return self._pet.GetPetById(pet_pb2.GetPetByIdRequest(pet_id=pet_id), timeout=10)

    def close(self) -> None:
        """Close underlying gRPC channel."""
        self._channel.close()


class EnvoyGrpcHttpClient(BasePetstoreClient):
    """HTTP-framed gRPC transport client (through Envoy)."""

    transport_name = "envoy"

    def __init__(self, base_url: str) -> None:
        """Create Envoy client bound to http://host:port base URL."""
        self._base_url = base_url.rstrip("/")

    def _unary(
        self,
        method_path: str,
        request_msg: Message,
        response_type: type[Message],
    ) -> Message:
        """Execute unary gRPC method using protobuf wire framing."""
        url = f"{self._base_url}{method_path}"
        payload = request_msg.SerializeToString()
        frame = b"\x00" + len(payload).to_bytes(4, byteorder="big") + payload
        request = Request(
            url,
            data=frame,
            headers={"content-type": "application/grpc", "te": "trailers"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=10) as response:
                body = response.read()
                grpc_status = response.headers.get("grpc-status", "0")
                grpc_message = response.headers.get("grpc-message", "")
        except HTTPError as exc:  # pragma: no cover - surfaced to caller
            raise RuntimeError(f"HTTP {exc.code} while calling {method_path}") from exc
        except URLError as exc:  # pragma: no cover - surfaced to caller
            raise RuntimeError(f"Network error while calling {method_path}: {exc.reason}") from exc

        if grpc_status not in ("", "0"):
            raise RuntimeError(f"gRPC status {grpc_status}: {grpc_message}")
        if len(body) < 5:
            raise RuntimeError("Invalid gRPC frame: body shorter than 5-byte header")
        if body[0] != 0:
            raise RuntimeError(f"Compressed frame not supported for test client: flag={body[0]}")

        declared_len = int.from_bytes(body[1:5], byteorder="big")
        msg = body[5 : 5 + declared_len]
        return response_type.FromString(msg)

    def health_check(self) -> health_pb2.HealthResponse:
        """Run health check through Envoy."""
        return self._unary(
            "/petstore.v1.Health/Check",
            health_pb2.HealthRequest(),
            health_pb2.HealthResponse,
        )

    def list_available_pets(self, limit: int = 10) -> pet_pb2.FindPetsByStatusResponse:
        """List available pets through Envoy."""
        return self._unary(
            "/petstore.v1.PetService/FindPetsByStatus",
            pet_pb2.FindPetsByStatusRequest(
                status=common_pb2.PET_STATUS_AVAILABLE,
                limit=limit,
            ),
            pet_pb2.FindPetsByStatusResponse,
        )

    def get_pet(self, pet_id: int) -> pet_pb2.GetPetByIdResponse:
        """Fetch one pet by id through Envoy."""
        return self._unary(
            "/petstore.v1.PetService/GetPetById",
            pet_pb2.GetPetByIdRequest(pet_id=pet_id),
            pet_pb2.GetPetByIdResponse,
        )

    def close(self) -> None:
        """No-op close for urllib-based client."""


def create_client(transport: str, targets: ClientTargets) -> BasePetstoreClient:
    """Create a transport client by name."""
    if transport == "grpc":
        return GrpcPetstoreClient(targets.grpc_target)
    if transport == "envoy":
        return EnvoyGrpcHttpClient(targets.envoy_base_url)
    raise ValueError(f"Unknown transport: {transport}")
