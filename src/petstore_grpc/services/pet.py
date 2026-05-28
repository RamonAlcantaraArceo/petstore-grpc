"""gRPC PetService adapter backed by petstore_core services."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

import grpc
from petstore_core.errors import DomainError
from petstore_core.repositories.postgres.pet import PostgresPetRepository
from petstore_core.schemas.pet import Category, Pet, PetCreate, PetStatus, PetUpdate, Tag
from petstore_core.services.pet import PetService

from petstore_grpc.db import get_session
from petstore_grpc.generated.petstore.v1 import common_pb2, pet_pb2, pet_pb2_grpc
from petstore_grpc.services._memory import get_memory_pet_repo
from petstore_grpc.services.error_mapping import abort_for_domain_error

_PROTO_TO_PET_STATUS: dict[int, PetStatus] = {
    common_pb2.PET_STATUS_AVAILABLE: PetStatus.available,
    common_pb2.PET_STATUS_PENDING: PetStatus.pending,
    common_pb2.PET_STATUS_SOLD: PetStatus.sold,
}

_PET_STATUS_TO_PROTO: dict[PetStatus, int] = {v: k for k, v in _PROTO_TO_PET_STATUS.items()}


def _proto_to_category(cat_msg: common_pb2.Category) -> Category | None:
    """Convert a proto Category message to a core Category schema."""
    return Category(
        id=cat_msg.id if cat_msg.HasField("id") else None,
        name=cat_msg.name if cat_msg.HasField("name") else None,
    )


def _proto_to_tags(tags: list[common_pb2.Tag]) -> list[Tag]:
    """Convert repeated proto Tag messages to core Tag schemas."""
    return [
        Tag(
            id=t.id if t.HasField("id") else None,
            name=t.name if t.HasField("name") else None,
        )
        for t in tags
    ]


def _schema_to_proto_pet(pet: Pet) -> common_pb2.Pet:
    """Convert a core Pet schema to a proto Pet message."""
    proto = common_pb2.Pet(
        name=pet.name,
        photo_urls=list(pet.photo_urls or []),
        status=_PET_STATUS_TO_PROTO.get(pet.status, common_pb2.PET_STATUS_UNSPECIFIED),
    )
    if pet.id is not None:
        proto.id = pet.id
    if pet.category is not None:
        cat = common_pb2.Category()
        if pet.category.id is not None:
            cat.id = pet.category.id
        if pet.category.name is not None:
            cat.name = pet.category.name
        proto.category.CopyFrom(cat)
    for t in pet.tags or []:
        tag = common_pb2.Tag()
        if t.id is not None:
            tag.id = t.id
        if t.name is not None:
            tag.name = t.name
        proto.tags.append(tag)
    return proto


class PetServicer(pet_pb2_grpc.PetServiceServicer):
    """gRPC PetService adapter backed by core repositories."""

    @asynccontextmanager
    async def _service(self):
        """Yield a PetService backed by the configured storage mode."""
        if os.environ.get("STORAGE_MODE", "memory") == "memory":
            yield PetService(get_memory_pet_repo())
            return

        async with get_session() as session:
            yield PetService(
                PostgresPetRepository(session),
                commit=session.commit,
                rollback=session.rollback,
            )

    async def AddPet(
        self,
        request: pet_pb2.AddPetRequest,
        context: grpc.aio.ServicerContext,
    ) -> pet_pb2.AddPetResponse:
        """Create a new pet."""
        p = request.pet
        create = PetCreate(
            name=p.name,
            photo_urls=list(p.photo_urls),
            category=_proto_to_category(p.category) if p.HasField("category") else None,
            tags=_proto_to_tags(p.tags),
            status=_PROTO_TO_PET_STATUS.get(p.status),
        )
        async with self._service() as service:
            try:
                pet = await service.add_pet(create)
            except DomainError as exc:
                await abort_for_domain_error(context, exc)
        return pet_pb2.AddPetResponse(pet=_schema_to_proto_pet(pet))

    async def UpdatePet(
        self,
        request: pet_pb2.UpdatePetRequest,
        context: grpc.aio.ServicerContext,
    ) -> pet_pb2.UpdatePetResponse:
        """Update an existing pet."""
        p = request.pet
        if not p.HasField("id"):
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "pet.id is required")
        update = PetUpdate(
            id=p.id,
            name=p.name,
            photo_urls=list(p.photo_urls),
            category=_proto_to_category(p.category) if p.HasField("category") else None,
            tags=_proto_to_tags(p.tags),
            status=_PROTO_TO_PET_STATUS.get(p.status),
        )
        async with self._service() as service:
            try:
                pet = await service.update_pet(update)
            except DomainError as exc:
                await abort_for_domain_error(context, exc)
        return pet_pb2.UpdatePetResponse(pet=_schema_to_proto_pet(pet))

    async def FindPetsByStatus(
        self,
        request: pet_pb2.FindPetsByStatusRequest,
        context: grpc.aio.ServicerContext,
    ) -> pet_pb2.FindPetsByStatusResponse:
        """List pets filtered by status."""
        status = _PROTO_TO_PET_STATUS.get(request.status)
        status_str = status.value if status else None
        limit = request.limit or None
        async with self._service() as service:
            pets = await service.find_by_status(status_str, skip=request.skip, limit=limit)
        return pet_pb2.FindPetsByStatusResponse(pets=[_schema_to_proto_pet(p) for p in pets])

    async def FindPetsByTags(
        self,
        request: pet_pb2.FindPetsByTagsRequest,
        context: grpc.aio.ServicerContext,
    ) -> pet_pb2.FindPetsByTagsResponse:
        """List pets filtered by tag names."""
        async with self._service() as service:
            pets = await service.find_by_tags(list(request.tags))
        return pet_pb2.FindPetsByTagsResponse(pets=[_schema_to_proto_pet(p) for p in pets])

    async def GetPetById(
        self,
        request: pet_pb2.GetPetByIdRequest,
        context: grpc.aio.ServicerContext,
    ) -> pet_pb2.GetPetByIdResponse:
        """Get a pet by ID."""
        async with self._service() as service:
            try:
                pet = await service.get_pet(request.pet_id)
            except DomainError as exc:
                await abort_for_domain_error(context, exc)
        return pet_pb2.GetPetByIdResponse(pet=_schema_to_proto_pet(pet))

    async def UpdatePetWithForm(
        self,
        request: pet_pb2.UpdatePetWithFormRequest,
        context: grpc.aio.ServicerContext,
    ) -> pet_pb2.UpdatePetWithFormResponse:
        """Update a pet's name and/or status via form fields."""
        new_name = request.name if request.HasField("name") else None
        new_status = None
        if request.HasField("status"):
            try:
                new_status = PetStatus(request.status).value
            except ValueError:
                new_status = None

        async with self._service() as service:
            try:
                updated = await service.update_pet_with_form(
                    request.pet_id,
                    name=new_name,
                    status=new_status,
                )
            except DomainError as exc:
                await abort_for_domain_error(context, exc)
        return pet_pb2.UpdatePetWithFormResponse(pet=_schema_to_proto_pet(updated))

    async def DeletePet(
        self,
        request: pet_pb2.DeletePetRequest,
        context: grpc.aio.ServicerContext,
    ) -> pet_pb2.DeletePetResponse:
        """Delete a pet by ID."""
        async with self._service() as service:
            try:
                await service.delete_pet(request.pet_id)
            except DomainError as exc:
                await abort_for_domain_error(context, exc)
        return pet_pb2.DeletePetResponse(message={"result": "ok"})

    async def UploadFile(
        self,
        request_iterator: grpc.aio.ServicerContext,
        context: grpc.aio.ServicerContext,
    ) -> pet_pb2.UploadFileResponse:
        """File upload is not supported."""
        await context.abort(grpc.StatusCode.UNIMPLEMENTED, "UploadFile is not implemented")
