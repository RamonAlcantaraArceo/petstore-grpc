"""Integration tests for server startup and gRPC communication."""

import grpc
import pytest

from petstore_grpc.generated.petstore.v1 import health_pb2, health_pb2_grpc


@pytest.mark.asyncio
async def test_server_startup_and_health_check(grpc_channel: grpc.aio.Channel):
    """Test that server starts and responds to health check RPC.

    Args:
        grpc_channel: Client channel to the test server.
    """
    stub = health_pb2_grpc.HealthStub(grpc_channel)
    request = health_pb2.HealthRequest()

    response = await stub.Check(request)

    assert response.status == "SERVING"
    assert response.mode == "dev"  # Default mode
    assert response.details.version == "0.1.0"
    assert isinstance(response.details.build_date, str)
    assert isinstance(response.details.git_commit_sha, str)
