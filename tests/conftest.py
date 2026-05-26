"""Shared pytest fixtures."""

from collections.abc import AsyncIterator

import grpc
import pytest

from petstore_grpc.generated.petstore.v1 import health_pb2_grpc
from petstore_grpc.services.health import HealthServicer


@pytest.fixture
async def grpc_server() -> AsyncIterator[tuple[grpc.aio.Server, int]]:
    """Create an in-process gRPC server for testing.

    Yields:
        Tuple of (running gRPC server instance, port number).
    """
    server = grpc.aio.server()
    health_pb2_grpc.add_HealthServicer_to_server(HealthServicer(), server)
    port = server.add_insecure_port("localhost:0")  # Ephemeral port

    await server.start()
    yield server, port
    await server.stop(grace=0)


@pytest.fixture
async def grpc_channel(
    grpc_server: tuple[grpc.aio.Server, int],
) -> AsyncIterator[grpc.aio.Channel]:
    """Create a gRPC channel connected to the test server.

    Args:
        grpc_server: Tuple of (server, port) from grpc_server fixture.

    Yields:
        Client channel to the server.
    """
    _, port = grpc_server
    async with grpc.aio.insecure_channel(f"localhost:{port}") as channel:
        yield channel
