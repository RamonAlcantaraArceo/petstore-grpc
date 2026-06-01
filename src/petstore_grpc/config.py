"""Configuration loader for petstore-grpc service."""

import functools
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Service configuration settings.

    Attributes:
        storage_mode: Storage Mode (memory, local, cloud)
        port: gRPC server port
        build_date: Build timestamp (injected by Docker)
        git_commit_sha: Git commit SHA (injected by Docker)
    """

    storage_mode: str
    port: int
    build_date: str
    git_commit_sha: str

    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from environment variables.

        Returns:
            Settings instance populated from environment.
        """
        return cls(
            storage_mode=os.environ.get("STORAGE_MODE", "memory"),
            port=int(os.environ.get("PORT", "50051")),
            build_date=os.environ.get("BUILD_DATE", "unknown"),
            git_commit_sha=os.environ.get("GIT_COMMIT_SHA", os.environ.get("GIT_SHA", "unknown")),
        )


@functools.lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings singleton.

    Returns:
        Settings instance.
    """
    return Settings.from_env()
