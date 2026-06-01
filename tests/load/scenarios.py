"""Core load scenarios for Petstore transport paths."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LoadScenario:
    """A concise, named load scenario."""

    name: str
    transport: str
    operation: str
    target_rps: int
    description: str


CORE_SCENARIOS: tuple[LoadScenario, ...] = (
    LoadScenario(
        name="grpc-health-smoke",
        transport="grpc",
        operation="Health/Check",
        target_rps=25,
        description="Verify low-latency control-plane health checks through native gRPC.",
    ),
    LoadScenario(
        name="grpc-list-pets",
        transport="grpc",
        operation="PetService/FindPetsByStatus",
        target_rps=20,
        description="Exercise main read path over native gRPC with seeded dataset.",
    ),
    LoadScenario(
        name="envoy-health-smoke",
        transport="envoy",
        operation="Health/Check",
        target_rps=25,
        description="Validate Envoy forwarding overhead for health checks.",
    ),
    LoadScenario(
        name="envoy-list-pets",
        transport="envoy",
        operation="PetService/FindPetsByStatus",
        target_rps=20,
        description="Exercise Envoy-framed gRPC read path under concurrent load.",
    ),
)
