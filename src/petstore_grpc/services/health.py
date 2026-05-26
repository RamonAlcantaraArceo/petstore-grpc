"""Health check service implementation."""

import importlib.metadata
import logging

import grpc

from petstore_grpc.config import get_settings
from petstore_grpc.generated.petstore.v1 import health_pb2, health_pb2_grpc

logger = logging.getLogger(__name__)


class HealthServicer(health_pb2_grpc.HealthServicer):
    """Health check servicer implementation.

    Provides service health status and build metadata via the Health/Check RPC.
    """

    async def Check(
        self,
        request: health_pb2.HealthRequest,
        context: grpc.aio.ServicerContext,
    ) -> health_pb2.HealthResponse:
        """Handle health check request.

        Args:
            request: Empty HealthRequest message.
            context: gRPC servicer context.

        Returns:
            HealthResponse with status, mode, and build details.
        """
        settings = get_settings()
        version = importlib.metadata.version("petstore-grpc")

        response = health_pb2.HealthResponse(
            status="SERVING",
            mode=settings.mode,
            details=health_pb2.HealthResponse.Details(
                version=version,
                build_date=settings.build_date,
                git_commit_sha=settings.git_commit_sha,
            ),
        )

        logger.debug("Health check: status=%s, version=%s", response.status, version)
        return response
