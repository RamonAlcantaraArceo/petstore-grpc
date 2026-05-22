"""Shared pytest fixtures."""

import asyncio
from typing import AsyncIterator

import grpc
import pytest

from petstore_grpc.generated.petstore.v1 import health_pb2_grpc
from petstore_grpc.services.health import HealthServicer


@pytest.fixture
async def grpc_server() -> AsyncIterator[grpc.aio.Server]:
    """Create an in-process gRPC server for testing.

    Yields:
        Running gRPC server instance.
    """
    server = grpc.aio.server()
    health_pb2_grpc.add_HealthServicer_to_server(HealthServicer(), server)
    port = server.add_insecure_port("localhost:0")  # Ephemeral port

    await server.start()
    yield server
    await server.stop(grace=0)


@pytest.fixture
async def grpc_channel(grpc_server: grpc.aio.Server) -> AsyncIterator[grpc.aio.Channel]:
    """Create a gRPC channel connected to the test server.

    Args:
        grpc_server: The running test server.

    Yields:
        Client channel to the server.
    """
    # Extract the actual port bound by the server
    port = list(grpc_server._server._state.server_ports)[0]
    async with grpc.aio.insecure_channel(f"localhost:{port}") as channel:
        yield channel
