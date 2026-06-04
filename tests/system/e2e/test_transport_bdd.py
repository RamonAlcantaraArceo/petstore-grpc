"""BDD scenarios for transport parity."""

from __future__ import annotations

import os
from collections.abc import Generator

import allure
import pytest
from pytest_bdd import given, parsers, scenario, then, when

from petstore_grpc.generated.petstore.v1 import common_pb2, health_pb2, pet_pb2
from tests.system.e2e.clients import BasePetstoreClient, ClientTargets, create_client
from tests.system.e2e.conftest import _parse_transports


@pytest.fixture
def transport_client(
    transport: str,
    e2e_targets: ClientTargets,
) -> Generator[BasePetstoreClient, None, None]:
    """Create per-scenario client based on Scenario Outline transport."""
    if os.getenv("RUN_E2E") != "1":
        pytest.skip("Set RUN_E2E=1 to run system/e2e tests")

    if transport not in _parse_transports():
        pytest.fail(f"Transport {transport!r} not enabled in E2E_TRANSPORTS")

    client = create_client(transport, e2e_targets)
    try:
        client.health_check()
    except Exception as exc:  # noqa: BLE001
        client.close()
        pytest.skip(f"{transport} endpoint unavailable: {exc}")
    yield client
    client.close()


@allure.id("BDD-TRANSPORT-HEALTH-001")
@pytest.mark.system
@pytest.mark.e2e
@pytest.mark.bdd
@scenario("features/petstore_transport.feature", "Health endpoint returns SERVING")
def test_bdd_health() -> None:
    """BDD scenario for health parity."""


@allure.id("BDD-TRANSPORT-PET-LIST-001")
@pytest.mark.system
@pytest.mark.e2e
@pytest.mark.bdd
@scenario("features/petstore_transport.feature", "Available pets are reachable from seeded data")
def test_bdd_available_pets() -> None:
    """BDD scenario for seeded pet availability parity."""


@given(parsers.parse('a "{transport}" client'), target_fixture="transport")
def given_transport(transport: str) -> str:
    """Expose transport example value as fixture."""
    return transport


@when("I execute a health check", target_fixture="health_response")
def when_health_check(transport_client: BasePetstoreClient) -> health_pb2.HealthResponse:
    """Execute health check through selected transport."""
    return transport_client.health_check()


@then("the service reports serving")
def then_serving(health_response: health_pb2.HealthResponse) -> None:
    """Verify health response is SERVING."""
    assert health_response.status == "SERVING"


@when("I request available pets", target_fixture="pet_list_response")
def when_list_pets(transport_client: BasePetstoreClient) -> pet_pb2.FindPetsByStatusResponse:
    """Fetch available pets through selected transport."""
    return transport_client.list_available_pets(limit=20)


@then("I receive at least one available pet")
def then_available_pets(pet_list_response: pet_pb2.FindPetsByStatusResponse) -> None:
    """Verify seeded available pets are returned."""
    assert len(pet_list_response.pets) > 0
    assert all(pet.status == common_pb2.PET_STATUS_AVAILABLE for pet in pet_list_response.pets)
