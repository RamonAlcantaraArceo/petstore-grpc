"""Shared in-memory repository singletons for gRPC services."""

from __future__ import annotations

from petstore_core.repositories.memory.order import MemoryOrderRepository
from petstore_core.repositories.memory.pet import MemoryPetRepository
from petstore_core.repositories.memory.user import MemoryUserRepository

_memory_pet_repo: MemoryPetRepository | None = None
_memory_order_repo: MemoryOrderRepository | None = None
_memory_user_repo: MemoryUserRepository | None = None


def get_memory_pet_repo() -> MemoryPetRepository:
    """Return the shared in-memory pet repository singleton."""
    global _memory_pet_repo
    if _memory_pet_repo is None:
        _memory_pet_repo = MemoryPetRepository()
    return _memory_pet_repo


def get_memory_order_repo() -> MemoryOrderRepository:
    """Return the shared in-memory order repository singleton."""
    global _memory_order_repo
    if _memory_order_repo is None:
        _memory_order_repo = MemoryOrderRepository()
    return _memory_order_repo


def get_memory_user_repo() -> MemoryUserRepository:
    """Return the shared in-memory user repository singleton."""
    global _memory_user_repo
    if _memory_user_repo is None:
        _memory_user_repo = MemoryUserRepository()
    return _memory_user_repo

