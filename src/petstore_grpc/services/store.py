"""gRPC StoreService implementation backed by PostgresOrderRepository."""

from __future__ import annotations

from datetime import UTC

import grpc
from app.repositories.postgres.order import PostgresOrderRepository
from app.schemas.order import Order, OrderCreate, OrderStatus
from google.protobuf.timestamp_pb2 import Timestamp

from petstore_grpc.db import get_session
from petstore_grpc.generated.petstore.v1 import common_pb2, store_pb2, store_pb2_grpc

_PROTO_TO_ORDER_STATUS: dict[int, OrderStatus] = {
    common_pb2.ORDER_STATUS_PLACED: OrderStatus.placed,
    common_pb2.ORDER_STATUS_APPROVED: OrderStatus.approved,
    common_pb2.ORDER_STATUS_DELIVERED: OrderStatus.delivered,
}

_ORDER_STATUS_TO_PROTO: dict[OrderStatus, int] = {v: k for k, v in _PROTO_TO_ORDER_STATUS.items()}


def _schema_to_proto_order(order: Order) -> common_pb2.Order:
    """Convert a petstore-api Order schema to a proto Order message.

    Args:
        order: An Order Pydantic schema.

    Returns:
        A proto Order message.
    """
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
    """gRPC StoreService implementation backed by PostgresOrderRepository."""

    async def GetInventory(
        self,
        request: store_pb2.GetInventoryRequest,
        context: grpc.aio.ServicerContext,
    ) -> store_pb2.GetInventoryResponse:
        """Return all orders as inventory.

        Args:
            request: Empty GetInventoryRequest.
            context: gRPC servicer context.

        Returns:
            GetInventoryResponse with all orders.
        """
        async with get_session() as session:
            orders = await PostgresOrderRepository(session).get_inventory()
        return store_pb2.GetInventoryResponse(orders=[_schema_to_proto_order(o) for o in orders])

    async def PlaceOrder(
        self,
        request: store_pb2.PlaceOrderRequest,
        context: grpc.aio.ServicerContext,
    ) -> store_pb2.PlaceOrderResponse:
        """Place a new order.

        Args:
            request: PlaceOrderRequest containing the order to create.
            context: gRPC servicer context.

        Returns:
            PlaceOrderResponse with the created order.
        """
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
        async with get_session() as session:
            order = await PostgresOrderRepository(session).create(create)
        return store_pb2.PlaceOrderResponse(order=_schema_to_proto_order(order))

    async def GetOrderById(
        self,
        request: store_pb2.GetOrderByIdRequest,
        context: grpc.aio.ServicerContext,
    ) -> store_pb2.GetOrderByIdResponse:
        """Get an order by ID.

        Args:
            request: GetOrderByIdRequest with the order ID.
            context: gRPC servicer context.

        Returns:
            GetOrderByIdResponse with the order.
        """
        async with get_session() as session:
            order = await PostgresOrderRepository(session).get(request.order_id)
        if order is None:
            await context.abort(grpc.StatusCode.NOT_FOUND, f"Order {request.order_id} not found")
        return store_pb2.GetOrderByIdResponse(order=_schema_to_proto_order(order))

    async def DeleteOrder(
        self,
        request: store_pb2.DeleteOrderRequest,
        context: grpc.aio.ServicerContext,
    ) -> store_pb2.DeleteOrderResponse:
        """Delete an order by ID.

        Args:
            request: DeleteOrderRequest with the order ID.
            context: gRPC servicer context.

        Returns:
            DeleteOrderResponse with confirmation.
        """
        async with get_session() as session:
            try:
                await PostgresOrderRepository(session).delete(request.order_id)
            except KeyError:
                await context.abort(
                    grpc.StatusCode.NOT_FOUND, f"Order {request.order_id} not found"
                )
        return store_pb2.DeleteOrderResponse(message={"result": "ok"})
