"""System/e2e parity tests across native gRPC and Envoy transport."""

from __future__ import annotations

import importlib.metadata

import allure
import pytest

from petstore_grpc.generated.petstore.v1 import common_pb2
from tests.system.e2e.clients import BasePetstoreClient


@pytest.mark.system
@pytest.mark.e2e
@allure.id("E2E-TRANSPORT-HEALTH-001")
@pytest.mark.parametrize("client", ["grpc", "envoy"], indirect=True)
def test_health_check_returns_serving(client: BasePetstoreClient) -> None:
    """Validate both transport clients return healthy status."""
    response = client.health_check()

    assert response.status == "SERVING"
    assert response.details.version == importlib.metadata.version("petstore-grpc")


@pytest.mark.system
@pytest.mark.e2e
@allure.id("E2E-TRANSPORT-PET-LIST-001")
@pytest.mark.parametrize("client", ["grpc", "envoy"], indirect=True)
def test_available_pets_are_listed(client: BasePetstoreClient) -> None:
    """Validate both transport clients can list seeded available pets."""
    response = client.list_available_pets(limit=20)

    assert len(response.pets) > 0
    assert all(pet.status == common_pb2.PET_STATUS_AVAILABLE for pet in response.pets)


@pytest.mark.system
@pytest.mark.e2e
@allure.id("E2E-TRANSPORT-PET-GET-001")
@pytest.mark.parametrize("client", ["grpc", "envoy"], indirect=True)
def test_get_pet_round_trip(client: BasePetstoreClient) -> None:
    """Validate get-by-id works for both transport clients."""
    listed = client.list_available_pets(limit=1)
    pet_id = int(listed.pets[0].id)

    response = client.get_pet(pet_id)

    assert int(response.pet.id) == pet_id
    assert response.pet.name

