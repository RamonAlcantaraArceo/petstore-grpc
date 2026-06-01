import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PetStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PET_STATUS_UNSPECIFIED: _ClassVar[PetStatus]
    PET_STATUS_AVAILABLE: _ClassVar[PetStatus]
    PET_STATUS_PENDING: _ClassVar[PetStatus]
    PET_STATUS_SOLD: _ClassVar[PetStatus]

class OrderStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ORDER_STATUS_UNSPECIFIED: _ClassVar[OrderStatus]
    ORDER_STATUS_PLACED: _ClassVar[OrderStatus]
    ORDER_STATUS_APPROVED: _ClassVar[OrderStatus]
    ORDER_STATUS_DELIVERED: _ClassVar[OrderStatus]

PET_STATUS_UNSPECIFIED: PetStatus
PET_STATUS_AVAILABLE: PetStatus
PET_STATUS_PENDING: PetStatus
PET_STATUS_SOLD: PetStatus
ORDER_STATUS_UNSPECIFIED: OrderStatus
ORDER_STATUS_PLACED: OrderStatus
ORDER_STATUS_APPROVED: OrderStatus
ORDER_STATUS_DELIVERED: OrderStatus

class Category(_message.Message):
    __slots__ = ("id", "name")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class Tag(_message.Message):
    __slots__ = ("id", "name")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class Pet(_message.Message):
    __slots__ = ("id", "name", "photo_urls", "category", "tags", "status")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PHOTO_URLS_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    photo_urls: _containers.RepeatedScalarFieldContainer[str]
    category: Category
    tags: _containers.RepeatedCompositeFieldContainer[Tag]
    status: PetStatus
    def __init__(
        self,
        id: _Optional[int] = ...,
        name: _Optional[str] = ...,
        photo_urls: _Optional[_Iterable[str]] = ...,
        category: _Optional[_Union[Category, _Mapping]] = ...,
        tags: _Optional[_Iterable[_Union[Tag, _Mapping]]] = ...,
        status: _Optional[_Union[PetStatus, str]] = ...,
    ) -> None: ...

class Order(_message.Message):
    __slots__ = ("id", "pet_id", "quantity", "ship_date", "status", "complete")
    ID_FIELD_NUMBER: _ClassVar[int]
    PET_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    SHIP_DATE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    COMPLETE_FIELD_NUMBER: _ClassVar[int]
    id: int
    pet_id: int
    quantity: int
    ship_date: _timestamp_pb2.Timestamp
    status: OrderStatus
    complete: bool
    def __init__(
        self,
        id: _Optional[int] = ...,
        pet_id: _Optional[int] = ...,
        quantity: _Optional[int] = ...,
        ship_date: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...,
        status: _Optional[_Union[OrderStatus, str]] = ...,
        complete: bool = ...,
    ) -> None: ...

class User(_message.Message):
    __slots__ = ("id", "username", "first_name", "last_name", "email", "phone", "user_status")
    ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    USER_STATUS_FIELD_NUMBER: _ClassVar[int]
    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    phone: str
    user_status: int
    def __init__(
        self,
        id: _Optional[int] = ...,
        username: _Optional[str] = ...,
        first_name: _Optional[str] = ...,
        last_name: _Optional[str] = ...,
        email: _Optional[str] = ...,
        phone: _Optional[str] = ...,
        user_status: _Optional[int] = ...,
    ) -> None: ...
