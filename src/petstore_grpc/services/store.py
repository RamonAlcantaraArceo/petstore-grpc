"""gRPC StoreService adapter backed by petstore_core services."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import UTC

import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from petstore_core.errors import DomainError
from petstore_core.repositories.postgres.order import PostgresOrderRepository
from petstore_core.schemas.order import Order, OrderCreate, OrderStatus
from petstore_core.services.order import OrderService

from petstore_grpc.db import get_session
from petstore_grpc.generated.petstore.v1 import common_pb2, store_pb2, store_pb2_grpc
from petstore_grpc.services._memory import get_memory_order_repo
from petstore_grpc.services.error_mapping import abort_for_domain_error

_PROTO_TO_ORDER_STATUS: dict[int, OrderStatus] = {
    common_pb2.ORDER_STATUS_PLACED: OrderStatus.placed,
    common_pb2.ORDER_STATUS_APPROVED: OrderStatus.approved,
    common_pb2.ORDER_STATUS_DELIVERED: OrderStatus.delivered,
}

_ORDER_STATUS_TO_PROTO: dict[OrderStatus, int] = {v: k for k, v in _PROTO_TO_ORDER_STATUS.items()}


def _schema_to_proto_order(order: Order) -> common_pb2.Order:
    """Convert a core Order schema to a proto Order message."""
    proto = common_pb2.Order(
        status=_ORDER_STATUS_TO_PROTO.get(order.status, common_pb2.ORDER_STATUS_UNSPECIFIED),
        complete=bool(order.complete),
    )
    if order.id is not None:
        proto.id = order.id
    if order.pet_id is not None:
        proto.pet_id = order.pet_id
    if order.quantity is not None:
        proto.quantity = order.quantity
    if order.ship_date is not None:
        ts = Timestamp()
        ship_date = order.ship_date
        if ship_date.tzinfo is None:
            ship_date = ship_date.replace(tzinfo=UTC)
        ts.FromDatetime(ship_date)
        proto.ship_date.CopyFrom(ts)
    return proto


class StoreServicer(store_pb2_grpc.StoreServiceServicer):
    """gRPC StoreService adapter backed by core repositories."""

    @asynccontextmanager
    async def _service(self):
        """Yield an OrderService backed by the configured storage mode."""
        if os.environ.get("STORAGE_MODE", "memory") == "memory":
            yield OrderService(get_memory_order_repo())
            return

        async with get_session() as session:
            yield OrderService(
                PostgresOrderRepository(session),
                commit=session.commit,
                rollback=session.rollback,
            )

    async def GetInventory(
        self,
        request: store_pb2.GetInventoryRequest,
        context: grpc.aio.ServicerContext,
    ) -> store_pb2.GetInventoryResponse:
        """Return all orders as inventory."""
        async with self._service() as service:
            orders = await service.get_inventory()
        return store_pb2.GetInventoryResponse(orders=[_schema_to_proto_order(o) for o in orders])

    async def PlaceOrder(
        self,
        request: store_pb2.PlaceOrderRequest,
        context: grpc.aio.ServicerContext,
    ) -> store_pb2.PlaceOrderResponse:
        """Place a new order."""
        o = request.order
        ship_date = None
        if o.HasField("ship_date"):
            ship_date = o.ship_date.ToDatetime()

        create = OrderCreate(
            pet_id=o.pet_id if o.HasField("pet_id") else None,
            quantity=o.quantity if o.HasField("quantity") else None,
            ship_date=ship_date,
            status=_PROTO_TO_ORDER_STATUS.get(o.status),
            complete=o.complete,
        )
        async with self._service() as service:
            try:
                order = await service.place_order(create)
            except DomainError as exc:
                await abort_for_domain_error(context, exc)
        return store_pb2.PlaceOrderResponse(order=_schema_to_proto_order(order))

    async def GetOrderById(
        self,
        request: store_pb2.GetOrderByIdRequest,
        context: grpc.aio.ServicerContext,
    ) -> store_pb2.GetOrderByIdResponse:
        """Get an order by ID."""
        async with self._service() as service:
            try:
                order = await service.get_order(request.order_id)
            except DomainError as exc:
                await abort_for_domain_error(context, exc)
        return store_pb2.GetOrderByIdResponse(order=_schema_to_proto_order(order))

    async def DeleteOrder(
        self,
        request: store_pb2.DeleteOrderRequest,
        context: grpc.aio.ServicerContext,
    ) -> store_pb2.DeleteOrderResponse:
        """Delete an order by ID."""
        async with self._service() as service:
            try:
                await service.delete_order(request.order_id)
            except DomainError as exc:
                await abort_for_domain_error(context, exc)
        return store_pb2.DeleteOrderResponse(message={"result": "ok"})
