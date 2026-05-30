"""Locust scenarios for gRPC and Envoy transport load paths."""

from __future__ import annotations

import os
import time
from urllib.request import Request, urlopen

import grpc
from locust import HttpUser, User, between, task

from petstore_grpc.generated.petstore.v1 import (
    common_pb2,
    health_pb2,
    health_pb2_grpc,
    pet_pb2,
    pet_pb2_grpc,
)


def _fire_locust_event(
    user: User,
    request_type: str,
    name: str,
    started_at: float,
    response_length: int = 0,
    exception: Exception | None = None,
) -> None:
    """Emit request metrics to Locust."""
    elapsed_ms = (time.perf_counter() - started_at) * 1000
    user.environment.events.request.fire(
        request_type=request_type,
        name=name,
        response_time=elapsed_ms,
        response_length=response_length,
        exception=exception,
    )


class GrpcPetstoreUser(User):
    """Native gRPC Locust user."""

    wait_time = between(0.1, 1.0)
    abstract = False

    def on_start(self) -> None:
        """Create gRPC stubs."""
        target = os.getenv("LOCUST_GRPC_TARGET", "localhost:50051")
        self._channel = grpc.insecure_channel(target)
        self._health = health_pb2_grpc.HealthStub(self._channel)
        self._pet = pet_pb2_grpc.PetServiceStub(self._channel)

    def on_stop(self) -> None:
        """Close gRPC channel."""
        self._channel.close()

    @task(2)
    def health_check(self) -> None:
        """Load health endpoint."""
        started_at = time.perf_counter()
        try:
            response = self._health.Check(health_pb2.HealthRequest(), timeout=10)
            _fire_locust_event(
                self,
                request_type="grpc",
                name="Health/Check",
                started_at=started_at,
                response_length=len(response.SerializeToString()),
            )
        except Exception as exc:  # noqa: BLE001
            _fire_locust_event(
                self,
                request_type="grpc",
                name="Health/Check",
                started_at=started_at,
                exception=exc,
            )

    @task(3)
    def list_available_pets(self) -> None:
        """Load list-by-status endpoint."""
        started_at = time.perf_counter()
        try:
            response = self._pet.FindPetsByStatus(
                pet_pb2.FindPetsByStatusRequest(
                    status=common_pb2.PET_STATUS_AVAILABLE,
                    limit=20,
                ),
                timeout=10,
            )
            _fire_locust_event(
                self,
                request_type="grpc",
                name="PetService/FindPetsByStatus",
                started_at=started_at,
                response_length=len(response.SerializeToString()),
            )
        except Exception as exc:  # noqa: BLE001
            _fire_locust_event(
                self,
                request_type="grpc",
                name="PetService/FindPetsByStatus",
                started_at=started_at,
                exception=exc,
            )


class EnvoyGrpcHttpUser(HttpUser):
    """Envoy-framed gRPC Locust user over HTTP."""

    wait_time = between(0.1, 1.0)
    host = os.getenv("LOCUST_ENVOY_HOST", "http://localhost:8080")

    def _post_grpc(self, method_path: str, message: bytes, metric_name: str) -> None:
        """Send one unary gRPC frame over HTTP."""
        started_at = time.perf_counter()
        frame = b"\x00" + len(message).to_bytes(4, byteorder="big") + message
        request = Request(
            f"{self.host}{method_path}",
            data=frame,
            headers={"content-type": "application/grpc", "te": "trailers"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=10) as response:
                body = response.read()
                _fire_locust_event(
                    self,
                    request_type="grpc-http",
                    name=metric_name,
                    started_at=started_at,
                    response_length=len(body),
                )
        except Exception as exc:  # noqa: BLE001
            _fire_locust_event(
                self,
                request_type="grpc-http",
                name=metric_name,
                started_at=started_at,
                exception=exc,
            )

    @task(2)
    def health_check(self) -> None:
        """Load health endpoint through Envoy."""
        self._post_grpc(
            "/petstore.v1.Health/Check",
            health_pb2.HealthRequest().SerializeToString(),
            "Health/Check",
        )

    @task(3)
    def list_available_pets(self) -> None:
        """Load list-by-status endpoint through Envoy."""
        self._post_grpc(
            "/petstore.v1.PetService/FindPetsByStatus",
            pet_pb2.FindPetsByStatusRequest(
                status=common_pb2.PET_STATUS_AVAILABLE,
                limit=20,
            ).SerializeToString(),
            "PetService/FindPetsByStatus",
        )
