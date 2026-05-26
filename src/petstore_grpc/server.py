"""gRPC server bootstrap and lifecycle management."""

import asyncio
import logging
import os
import signal
import time

import grpc
from grpc_reflection.v1alpha import reflection

from petstore_grpc.config import get_settings
from petstore_grpc.generated.petstore.v1 import (
    health_pb2,
    health_pb2_grpc,
    pet_pb2,
    pet_pb2_grpc,
    store_pb2,
    store_pb2_grpc,
    user_pb2,
    user_pb2_grpc,
)
from petstore_grpc.services.health import HealthServicer
from petstore_grpc.services.pet import PetServicer
from petstore_grpc.services.store import StoreServicer
from petstore_grpc.services.user import UserServicer

logger = logging.getLogger(__name__)


class RequestLoggingInterceptor(grpc.aio.ServerInterceptor):
    """Log each RPC request that reaches this server."""

    async def intercept_service(self, continuation, handler_call_details):
        method = handler_call_details.method
        handler = await continuation(handler_call_details)

        if handler is None:
            logger.warning("RPC not handled: method=%s", method)
            return None

        if handler.unary_unary:
            original = handler.unary_unary

            async def wrapped(request, context):
                start = time.perf_counter()
                logger.info("RPC start: method=%s peer=%s", method, context.peer())
                try:
                    response = await original(request, context)
                except Exception:
                    elapsed_ms = (time.perf_counter() - start) * 1000
                    logger.exception("RPC error: method=%s duration_ms=%.1f", method, elapsed_ms)
                    raise

                elapsed_ms = (time.perf_counter() - start) * 1000
                code = context.code() or grpc.StatusCode.OK
                logger.info("RPC done: method=%s code=%s duration_ms=%.1f", method, code.name, elapsed_ms)
                return response

            return grpc.unary_unary_rpc_method_handler(
                wrapped,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        # Keep non-unary handlers unchanged; current API is unary-only.
        return handler


async def serve() -> None:
    """Start and run the gRPC server.

    Registers all servicers, binds to the configured port, and handles
    graceful shutdown on SIGTERM/SIGINT.
    """
    settings = get_settings()

    # Initialise DB when a backing store is configured
    if os.environ.get("STORAGE_MODE", "memory") != "memory":
        from petstore_grpc.db import ensure_db_schema, init_db

        init_db()
        await ensure_db_schema()
        logger.info("Database initialised")

    # Seed fixture data if SEED_DATASET is configured (works for both memory and postgres)
    if os.environ.get("SEED_DATASET"):
        from petstore_grpc.db import seed_db

        await seed_db()
        logger.info("Seed dataset '%s' applied", os.environ["SEED_DATASET"])

    server = grpc.aio.server(interceptors=[RequestLoggingInterceptor()])

    # Register servicers
    health_pb2_grpc.add_HealthServicer_to_server(HealthServicer(), server)
    pet_pb2_grpc.add_PetServiceServicer_to_server(PetServicer(), server)
    store_pb2_grpc.add_StoreServiceServicer_to_server(StoreServicer(), server)
    user_pb2_grpc.add_UserServiceServicer_to_server(UserServicer(), server)

    # Bind to all interfaces (IPv4 + IPv6 dual-stack) so Docker containers
    # can connect via host.docker.internal which may resolve to either family.
    listen_addr = f"[::]:{settings.port}"
    server.add_insecure_port(listen_addr)

    # Enable gRPC Server Reflection so tools (grpcurl) can introspect services
    try:
        service_names = (
            health_pb2.DESCRIPTOR.services_by_name["Health"].full_name,
            pet_pb2.DESCRIPTOR.services_by_name["PetService"].full_name,
            store_pb2.DESCRIPTOR.services_by_name["StoreService"].full_name,
            user_pb2.DESCRIPTOR.services_by_name["UserService"].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(service_names, server)
    except Exception:
        logger.exception("Failed to enable gRPC server reflection")

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
