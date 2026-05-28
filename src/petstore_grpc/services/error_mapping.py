"""Domain-to-gRPC error mapping helpers."""

from __future__ import annotations

import grpc
from petstore_core.errors import DomainError, NotFoundError, ValidationError


async def abort_for_domain_error(
    context: grpc.aio.ServicerContext,
    exc: DomainError,
) -> None:
    """Abort the RPC with a gRPC status code mapped from a domain error."""
    if isinstance(exc, NotFoundError):
        await context.abort(grpc.StatusCode.NOT_FOUND, str(exc))
    if isinstance(exc, ValidationError):
        await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(exc))
    await context.abort(grpc.StatusCode.UNKNOWN, str(exc))
