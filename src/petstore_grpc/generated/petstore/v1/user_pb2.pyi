from petstore.v1 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateUserRequest(_message.Message):
    __slots__ = ("user", "password")
    USER_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    user: _common_pb2.User
    password: str
    def __init__(
        self,
        user: _Optional[_Union[_common_pb2.User, _Mapping]] = ...,
        password: _Optional[str] = ...,
    ) -> None: ...

class CreateUserResponse(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: _common_pb2.User
    def __init__(self, user: _Optional[_Union[_common_pb2.User, _Mapping]] = ...) -> None: ...

class CreateUsersWithListRequest(_message.Message):
    __slots__ = ("users",)
    USERS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[CreateUserRequest]
    def __init__(
        self, users: _Optional[_Iterable[_Union[CreateUserRequest, _Mapping]]] = ...
    ) -> None: ...

class CreateUsersWithListResponse(_message.Message):
    __slots__ = ("users",)
    USERS_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[_common_pb2.User]
    def __init__(
        self, users: _Optional[_Iterable[_Union[_common_pb2.User, _Mapping]]] = ...
    ) -> None: ...

class LoginUserRequest(_message.Message):
    __slots__ = ("username", "password")
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    username: str
    password: str
    def __init__(self, username: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class LoginUserResponse(_message.Message):
    __slots__ = ("session",)
    class SessionEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

    SESSION_FIELD_NUMBER: _ClassVar[int]
    session: _containers.ScalarMap[str, str]
    def __init__(self, session: _Optional[_Mapping[str, str]] = ...) -> None: ...

class LogoutUserRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class LogoutUserResponse(_message.Message):
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

class GetUserByNameRequest(_message.Message):
    __slots__ = ("username",)
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    username: str
    def __init__(self, username: _Optional[str] = ...) -> None: ...

class GetUserByNameResponse(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: _common_pb2.User
    def __init__(self, user: _Optional[_Union[_common_pb2.User, _Mapping]] = ...) -> None: ...

class UpdateUserRequest(_message.Message):
    __slots__ = ("username", "user", "password")
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    username: str
    user: _common_pb2.User
    password: str
    def __init__(
        self,
        username: _Optional[str] = ...,
        user: _Optional[_Union[_common_pb2.User, _Mapping]] = ...,
        password: _Optional[str] = ...,
    ) -> None: ...

class UpdateUserResponse(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: _common_pb2.User
    def __init__(self, user: _Optional[_Union[_common_pb2.User, _Mapping]] = ...) -> None: ...

class DeleteUserRequest(_message.Message):
    __slots__ = ("username",)
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    username: str
    def __init__(self, username: _Optional[str] = ...) -> None: ...

class DeleteUserResponse(_message.Message):
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
