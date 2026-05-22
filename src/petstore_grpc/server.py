"""gRPC server bootstrap and lifecycle management."""

import asyncio
import logging
import signal

import grpc

from petstore_grpc.config import get_settings
from petstore_grpc.generated.petstore.v1 import health_pb2_grpc
from petstore_grpc.services.health import HealthServicer

logger = logging.getLogger(__name__)


async def serve() -> None:
    """Start and run the gRPC server.

    Registers all servicers, binds to the configured port, and handles
    graceful shutdown on SIGTERM/SIGINT.
    """
    settings = get_settings()
    server = grpc.aio.server()

    # Register servicers
    health_pb2_grpc.add_HealthServicer_to_server(HealthServicer(), server)

    # Bind to port
    listen_addr = f"0.0.0.0:{settings.port}"
    server.add_insecure_port(listen_addr)

    logger.info("Starting gRPC server on %s (mode=%s)", listen_addr, settings.mode)
    await server.start()

    # Graceful shutdown handler
    stop_event = asyncio.Event()

    def handle_signal(sig: int) -> None:
        logger.info("Received signal %d, initiating graceful shutdown", sig)
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda s=sig: handle_signal(s))

    await stop_event.wait()
    logger.info("Stopping server with 5s grace period")
    await server.stop(grace=5)
    logger.info("Server stopped")
