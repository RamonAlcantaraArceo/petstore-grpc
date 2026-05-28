"""gRPC UserService adapter backed by petstore_core services."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

import grpc
from petstore_core.errors import DomainError
from petstore_core.repositories.postgres.user import PostgresUserRepository
from petstore_core.schemas.user import User, UserCreate, UserUpdate
from petstore_core.services.user import UserService

from petstore_grpc.db import get_session
from petstore_grpc.generated.petstore.v1 import common_pb2, user_pb2, user_pb2_grpc
from petstore_grpc.services._memory import get_memory_user_repo
from petstore_grpc.services.error_mapping import abort_for_domain_error


def _schema_to_proto_user(user: User) -> common_pb2.User:
    """Convert a core User schema to a proto User message."""
    proto = common_pb2.User()
    if user.id is not None:
        proto.id = user.id
    if user.username is not None:
        proto.username = user.username
    if user.first_name is not None:
        proto.first_name = user.first_name
    if user.last_name is not None:
        proto.last_name = user.last_name
    if user.email is not None:
        proto.email = user.email
    if user.phone is not None:
        proto.phone = user.phone
    if user.user_status is not None:
        proto.user_status = user.user_status
    return proto


def _proto_to_user_create(req: user_pb2.CreateUserRequest) -> UserCreate:
    """Convert a CreateUserRequest to a core UserCreate schema."""
    u = req.user
    return UserCreate(
        username=u.username if u.HasField("username") else None,
        first_name=u.first_name if u.HasField("first_name") else None,
        last_name=u.last_name if u.HasField("last_name") else None,
        email=u.email if u.HasField("email") else None,
        phone=u.phone if u.HasField("phone") else None,
        user_status=u.user_status if u.HasField("user_status") else None,
        password=req.password if req.HasField("password") else None,
    )


class UserServicer(user_pb2_grpc.UserServiceServicer):
    """gRPC UserService adapter backed by core repositories."""

    @asynccontextmanager
    async def _service(self):
        """Yield a UserService backed by the configured storage mode."""
        if os.environ.get("STORAGE_MODE", "memory") == "memory":
            yield UserService(get_memory_user_repo())
            return

        async with get_session() as session:
            yield UserService(
                PostgresUserRepository(session),
                commit=session.commit,
                rollback=session.rollback,
            )

    async def CreateUser(
        self,
        request: user_pb2.CreateUserRequest,
        context: grpc.aio.ServicerContext,
    ) -> user_pb2.CreateUserResponse:
        """Create a single user."""
        create = _proto_to_user_create(request)
        async with self._service() as service:
            try:
                user = await service.create_user(create)
            except DomainError as exc:
                await abort_for_domain_error(context, exc)
        return user_pb2.CreateUserResponse(user=_schema_to_proto_user(user))

    async def CreateUsersWithList(
        self,
        request: user_pb2.CreateUsersWithListRequest,
        context: grpc.aio.ServicerContext,
    ) -> user_pb2.CreateUsersWithListResponse:
        """Create multiple users from a list."""
        creates = [_proto_to_user_create(r) for r in request.users]
        async with self._service() as service:
            try:
                users = await service.create_users_with_list(creates)
            except DomainError as exc:
                await abort_for_domain_error(context, exc)
        return user_pb2.CreateUsersWithListResponse(users=[_schema_to_proto_user(u) for u in users])

    async def LoginUser(
        self,
        request: user_pb2.LoginUserRequest,
        context: grpc.aio.ServicerContext,
    ) -> user_pb2.LoginUserResponse:
        """Authenticate a user and return a token."""
        async with self._service() as service:
            try:
                token = await service.login(request.username, request.password)
            except DomainError as exc:
                await abort_for_domain_error(context, exc)
        return user_pb2.LoginUserResponse(session={"token": token})

    async def LogoutUser(
        self,
        request: user_pb2.LogoutUserRequest,
        context: grpc.aio.ServicerContext,
    ) -> user_pb2.LogoutUserResponse:
        """Log out a user."""
        async with self._service() as service:
            await service.logout()
        return user_pb2.LogoutUserResponse(message={"result": "ok"})

    async def GetUserByName(
        self,
        request: user_pb2.GetUserByNameRequest,
        context: grpc.aio.ServicerContext,
    ) -> user_pb2.GetUserByNameResponse:
        """Get a user by username."""
        async with self._service() as service:
            try:
                user = await service.get_user(request.username)
            except DomainError as exc:
                await abort_for_domain_error(context, exc)
        return user_pb2.GetUserByNameResponse(user=_schema_to_proto_user(user))

    async def UpdateUser(
        self,
        request: user_pb2.UpdateUserRequest,
        context: grpc.aio.ServicerContext,
    ) -> user_pb2.UpdateUserResponse:
        """Update an existing user."""
        u = request.user
        update = UserUpdate(
            username=u.username if u.HasField("username") else None,
            first_name=u.first_name if u.HasField("first_name") else None,
            last_name=u.last_name if u.HasField("last_name") else None,
            email=u.email if u.HasField("email") else None,
            phone=u.phone if u.HasField("phone") else None,
            user_status=u.user_status if u.HasField("user_status") else None,
            password=request.password if request.HasField("password") else None,
        )
        async with self._service() as service:
            try:
                user = await service.update_user(request.username, update)
            except DomainError as exc:
                await abort_for_domain_error(context, exc)
        return user_pb2.UpdateUserResponse(user=_schema_to_proto_user(user))

    async def DeleteUser(
        self,
        request: user_pb2.DeleteUserRequest,
        context: grpc.aio.ServicerContext,
    ) -> user_pb2.DeleteUserResponse:
        """Delete a user by username."""
        async with self._service() as service:
            try:
                await service.delete_user(request.username)
            except DomainError as exc:
                await abort_for_domain_error(context, exc)
        return user_pb2.DeleteUserResponse(message={"result": "ok"})
