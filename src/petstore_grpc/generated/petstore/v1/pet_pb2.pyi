from petstore.v1 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AddPetRequest(_message.Message):
    __slots__ = ("pet",)
    PET_FIELD_NUMBER: _ClassVar[int]
    pet: _common_pb2.Pet
    def __init__(self, pet: _Optional[_Union[_common_pb2.Pet, _Mapping]] = ...) -> None: ...

class AddPetResponse(_message.Message):
    __slots__ = ("pet",)
    PET_FIELD_NUMBER: _ClassVar[int]
    pet: _common_pb2.Pet
    def __init__(self, pet: _Optional[_Union[_common_pb2.Pet, _Mapping]] = ...) -> None: ...

class UpdatePetRequest(_message.Message):
    __slots__ = ("pet",)
    PET_FIELD_NUMBER: _ClassVar[int]
    pet: _common_pb2.Pet
    def __init__(self, pet: _Optional[_Union[_common_pb2.Pet, _Mapping]] = ...) -> None: ...

class UpdatePetResponse(_message.Message):
    __slots__ = ("pet",)
    PET_FIELD_NUMBER: _ClassVar[int]
    pet: _common_pb2.Pet
    def __init__(self, pet: _Optional[_Union[_common_pb2.Pet, _Mapping]] = ...) -> None: ...

class FindPetsByStatusRequest(_message.Message):
    __slots__ = ("status", "skip", "limit")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SKIP_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.PetStatus
    skip: int
    limit: int
    def __init__(
        self,
        status: _Optional[_Union[_common_pb2.PetStatus, str]] = ...,
        skip: _Optional[int] = ...,
        limit: _Optional[int] = ...,
    ) -> None: ...

class FindPetsByStatusResponse(_message.Message):
    __slots__ = ("pets",)
    PETS_FIELD_NUMBER: _ClassVar[int]
    pets: _containers.RepeatedCompositeFieldContainer[_common_pb2.Pet]
    def __init__(
        self, pets: _Optional[_Iterable[_Union[_common_pb2.Pet, _Mapping]]] = ...
    ) -> None: ...

class FindPetsByTagsRequest(_message.Message):
    __slots__ = ("tags",)
    TAGS_FIELD_NUMBER: _ClassVar[int]
    tags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, tags: _Optional[_Iterable[str]] = ...) -> None: ...

class FindPetsByTagsResponse(_message.Message):
    __slots__ = ("pets",)
    PETS_FIELD_NUMBER: _ClassVar[int]
    pets: _containers.RepeatedCompositeFieldContainer[_common_pb2.Pet]
    def __init__(
        self, pets: _Optional[_Iterable[_Union[_common_pb2.Pet, _Mapping]]] = ...
    ) -> None: ...

class GetPetByIdRequest(_message.Message):
    __slots__ = ("pet_id",)
    PET_ID_FIELD_NUMBER: _ClassVar[int]
    pet_id: int
    def __init__(self, pet_id: _Optional[int] = ...) -> None: ...

class GetPetByIdResponse(_message.Message):
    __slots__ = ("pet",)
    PET_FIELD_NUMBER: _ClassVar[int]
    pet: _common_pb2.Pet
    def __init__(self, pet: _Optional[_Union[_common_pb2.Pet, _Mapping]] = ...) -> None: ...

class UpdatePetWithFormRequest(_message.Message):
    __slots__ = ("pet_id", "name", "status")
    PET_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    pet_id: int
    name: str
    status: str
    def __init__(
        self, pet_id: _Optional[int] = ..., name: _Optional[str] = ..., status: _Optional[str] = ...
    ) -> None: ...

class UpdatePetWithFormResponse(_message.Message):
    __slots__ = ("pet",)
    PET_FIELD_NUMBER: _ClassVar[int]
    pet: _common_pb2.Pet
    def __init__(self, pet: _Optional[_Union[_common_pb2.Pet, _Mapping]] = ...) -> None: ...

class DeletePetRequest(_message.Message):
    __slots__ = ("pet_id",)
    PET_ID_FIELD_NUMBER: _ClassVar[int]
    pet_id: int
    def __init__(self, pet_id: _Optional[int] = ...) -> None: ...

class DeletePetResponse(_message.Message):
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

class UploadFileRequest(_message.Message):
    __slots__ = ("pet_id", "file", "additional_metadata")
    PET_ID_FIELD_NUMBER: _ClassVar[int]
    FILE_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    pet_id: int
    file: bytes
    additional_metadata: str
    def __init__(
        self,
        pet_id: _Optional[int] = ...,
        file: _Optional[bytes] = ...,
        additional_metadata: _Optional[str] = ...,
    ) -> None: ...

class UploadFileResponse(_message.Message):
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
