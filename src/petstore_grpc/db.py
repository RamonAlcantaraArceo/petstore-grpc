"""Database session helpers that delegate to petstore-api's session module.

petstore-api owns the SQLAlchemy engine, session factory, and ORM models.
This module wires its settings and exposes a context-manager session helper
for use inside gRPC servicers.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from app.config import Settings as ApiSettings
from app.db.session import ensure_db_schema as _ensure_schema
from app.db.session import get_session_factory
from app.db.session import init_db as _init_db
from sqlalchemy.ext.asyncio import AsyncSession


def init_db() -> None:
    """Initialise the SQLAlchemy engine using petstore-api Settings from env."""
    _init_db(ApiSettings())


async def ensure_db_schema() -> None:
    """Create tables if they do not already exist (dev / test convenience)."""
    await _ensure_schema()


async def seed_db() -> None:
    """Seed the storage backend if ``SEED_DATASET`` env var is set.

    Delegates entirely to petstore-api's ``seed_from_settings`` which handles
    both ``memory`` and postgres storage modes.
    """
    from app.fixtures.loader import seed_from_settings

    await seed_from_settings(ApiSettings())


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield a transactional async database session.

    Commits on success, rolls back on any exception.

    Yields:
        An open AsyncSession.
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
