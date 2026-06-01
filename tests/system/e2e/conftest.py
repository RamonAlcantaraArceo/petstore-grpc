"""Fixtures for system/e2e transport tests."""

from __future__ import annotations

import os
from collections.abc import Generator

import pytest

from .clients import BasePetstoreClient, ClientTargets, create_client


def _parse_transports() -> list[str]:
    """Resolve enabled transports from E2E_TRANSPORTS."""
    raw = os.getenv("E2E_TRANSPORTS", "grpc,envoy")
    return [item.strip() for item in raw.split(",") if item.strip()]


@pytest.fixture(scope="session")
def e2e_targets() -> ClientTargets:
    """Resolve host/port targets for e2e runs."""
    return ClientTargets(
        grpc_target=os.getenv("E2E_GRPC_TARGET", "localhost:50051"),
        envoy_base_url=os.getenv("E2E_ENVOY_BASE_URL", "http://localhost:8080"),
    )


@pytest.fixture(scope="session")
def enabled_transports() -> list[str]:
    """Return the transport list under test."""
    return _parse_transports()


@pytest.fixture
def client(
    request: pytest.FixtureRequest, e2e_targets: ClientTargets
) -> Generator[BasePetstoreClient, None, None]:
    """Yield a transport-specific client and close it after the test."""
    if os.getenv("RUN_E2E") != "1":
        pytest.skip("Set RUN_E2E=1 to run system/e2e tests")

    transport = request.param
    instance = create_client(transport, e2e_targets)
    try:
        # Probe before each test so we skip cleanly when stack is not running.
        instance.health_check()
    except Exception as exc:  # noqa: BLE001
        instance.close()
        pytest.skip(f"{transport} endpoint unavailable: {exc}")
    yield instance
    instance.close()
