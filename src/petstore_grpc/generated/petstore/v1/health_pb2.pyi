from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HealthRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthResponse(_message.Message):
    __slots__ = ("status", "mode", "details")
    class Details(_message.Message):
        __slots__ = ("version", "build_date", "git_commit_sha")
        VERSION_FIELD_NUMBER: _ClassVar[int]
        BUILD_DATE_FIELD_NUMBER: _ClassVar[int]
        GIT_COMMIT_SHA_FIELD_NUMBER: _ClassVar[int]
        version: str
        build_date: str
        git_commit_sha: str
        def __init__(
            self,
            version: _Optional[str] = ...,
            build_date: _Optional[str] = ...,
            git_commit_sha: _Optional[str] = ...,
        ) -> None: ...

    STATUS_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    status: str
    mode: str
    details: HealthResponse.Details
    def __init__(
        self,
        status: _Optional[str] = ...,
        mode: _Optional[str] = ...,
        details: _Optional[_Union[HealthResponse.Details, _Mapping]] = ...,
    ) -> None: ...
