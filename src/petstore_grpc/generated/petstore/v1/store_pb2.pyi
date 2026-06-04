from petstore.v1 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetInventoryRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetInventoryResponse(_message.Message):
    __slots__ = ("orders",)
    ORDERS_FIELD_NUMBER: _ClassVar[int]
    orders: _containers.RepeatedCompositeFieldContainer[_common_pb2.Order]
    def __init__(
        self, orders: _Optional[_Iterable[_Union[_common_pb2.Order, _Mapping]]] = ...
    ) -> None: ...

class PlaceOrderRequest(_message.Message):
    __slots__ = ("order",)
    ORDER_FIELD_NUMBER: _ClassVar[int]
    order: _common_pb2.Order
    def __init__(self, order: _Optional[_Union[_common_pb2.Order, _Mapping]] = ...) -> None: ...

class PlaceOrderResponse(_message.Message):
    __slots__ = ("order",)
    ORDER_FIELD_NUMBER: _ClassVar[int]
    order: _common_pb2.Order
    def __init__(self, order: _Optional[_Union[_common_pb2.Order, _Mapping]] = ...) -> None: ...

class GetOrderByIdRequest(_message.Message):
    __slots__ = ("order_id",)
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    order_id: int
    def __init__(self, order_id: _Optional[int] = ...) -> None: ...

class GetOrderByIdResponse(_message.Message):
    __slots__ = ("order",)
    ORDER_FIELD_NUMBER: _ClassVar[int]
    order: _common_pb2.Order
    def __init__(self, order: _Optional[_Union[_common_pb2.Order, _Mapping]] = ...) -> None: ...

class DeleteOrderRequest(_message.Message):
    __slots__ = ("order_id",)
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    order_id: int
    def __init__(self, order_id: _Optional[int] = ...) -> None: ...

class DeleteOrderResponse(_message.Message):
    __slots__ = ("message",)
    class MessageEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: _containers.ScalarMap[str, str]
    def __init__(self, message: _Optional[_Mapping[str, str]] = ...) -> None: ...
