"""gRPC UserService implementation backed by PostgresUserRepository."""

from __future__ import annotations

import grpc
from app.repositories.postgres.user import PostgresUserRepository
from app.schemas.user import User, UserCreate, UserUpdate

from petstore_grpc.db import get_session
from petstore_grpc.generated.petstore.v1 import common_pb2, user_pb2, user_pb2_grpc


def _schema_to_proto_user(user: User) -> common_pb2.User:
    """Convert a petstore-api User schema to a proto User message.

    Args:
        user: A User Pydantic schema.

    Returns:
        A proto User message.
    """
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
    """Convert a CreateUserRequest to a UserCreate schema.

    Args:
        req: CreateUserRequest proto message.

    Returns:
        A UserCreate Pydantic schema.
    """
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
    """gRPC UserService implementation backed by PostgresUserRepository."""

    async def CreateUser(
        self,
        request: user_pb2.CreateUserRequest,
        context: grpc.aio.ServicerContext,
    ) -> user_pb2.CreateUserResponse:
        """Create a single user.

        Args:
            request: CreateUserRequest with user data and optional password.
            context: gRPC servicer context.

        Returns:
            CreateUserResponse with the created user.
        """
        create = _proto_to_user_create(request)
        async with get_session() as session:
            user = await PostgresUserRepository(session).create(create)
        return user_pb2.CreateUserResponse(user=_schema_to_proto_user(user))

    async def CreateUsersWithList(
        self,
        request: user_pb2.CreateUsersWithListRequest,
        context: grpc.aio.ServicerContext,
    ) -> user_pb2.CreateUsersWithListResponse:
        """Create multiple users from a list.

        Args:
            request: CreateUsersWithListRequest with multiple CreateUserRequests.
            context: gRPC servicer context.

        Returns:
            CreateUsersWithListResponse with all created users.
        """
        creates = [_proto_to_user_create(r) for r in request.users]
        async with get_session() as session:
            users = await PostgresUserRepository(session).create_many(creates)
        return user_pb2.CreateUsersWithListResponse(users=[_schema_to_proto_user(u) for u in users])

    async def LoginUser(
        self,
        request: user_pb2.LoginUserRequest,
        context: grpc.aio.ServicerContext,
    ) -> user_pb2.LoginUserResponse:
        """Login is not implemented (no auth layer).

        Args:
            request: LoginUserRequest (unused).
            context: gRPC servicer context.

        Returns:
            Never returns; aborts with UNIMPLEMENTED.
        """
        await context.abort(grpc.StatusCode.UNIMPLEMENTED, "LoginUser is not implemented")

    async def LogoutUser(
        self,
        request: user_pb2.LogoutUserRequest,
        context: grpc.aio.ServicerContext,
    ) -> user_pb2.LogoutUserResponse:
        """Logout is not implemented (no auth layer).

        Args:
            request: LogoutUserRequest (unused).
            context: gRPC servicer context.

        Returns:
            Never returns; aborts with UNIMPLEMENTED.
        """
        await context.abort(grpc.StatusCode.UNIMPLEMENTED, "LogoutUser is not implemented")

    async def GetUserByName(
        self,
        request: user_pb2.GetUserByNameRequest,
        context: grpc.aio.ServicerContext,
    ) -> user_pb2.GetUserByNameResponse:
        """Get a user by username.

        Args:
            request: GetUserByNameRequest with the username.
            context: gRPC servicer context.

        Returns:
            GetUserByNameResponse with the user.
        """
        async with get_session() as session:
            user = await PostgresUserRepository(session).get_by_username(request.username)
        if user is None:
            await context.abort(grpc.StatusCode.NOT_FOUND, f"User '{request.username}' not found")
        return user_pb2.GetUserByNameResponse(user=_schema_to_proto_user(user))

    async def UpdateUser(
        self,
        request: user_pb2.UpdateUserRequest,
        context: grpc.aio.ServicerContext,
    ) -> user_pb2.UpdateUserResponse:
        """Update an existing user.

        Args:
            request: UpdateUserRequest with current username, updated user data,
                and optional new password.
            context: gRPC servicer context.

        Returns:
            UpdateUserResponse with the updated user.
        """
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
        async with get_session() as session:
            try:
                user = await PostgresUserRepository(session).update(request.username, update)
            except KeyError:
                await context.abort(
                    grpc.StatusCode.NOT_FOUND, f"User '{request.username}' not found"
                )
        return user_pb2.UpdateUserResponse(user=_schema_to_proto_user(user))

    async def DeleteUser(
        self,
        request: user_pb2.DeleteUserRequest,
        context: grpc.aio.ServicerContext,
    ) -> user_pb2.DeleteUserResponse:
        """Delete a user by username.

        Args:
            request: DeleteUserRequest with the username.
            context: gRPC servicer context.

        Returns:
            DeleteUserResponse with confirmation.
        """
        async with get_session() as session:
            try:
                await PostgresUserRepository(session).delete(request.username)
            except KeyError:
                await context.abort(
                    grpc.StatusCode.NOT_FOUND, f"User '{request.username}' not found"
                )
        return user_pb2.DeleteUserResponse(message={"result": "ok"})
