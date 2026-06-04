"""Unit tests for the Health service."""

import importlib.metadata
import os
from unittest.mock import MagicMock

import grpc
import pytest

from petstore_grpc.config import get_settings
from petstore_grpc.generated.petstore.v1 import health_pb2
from petstore_grpc.services.health import HealthServicer


@pytest.mark.asyncio
async def test_health_check_returns_serving_status():
    """Test that health check returns SERVING status."""
    servicer = HealthServicer()
    request = health_pb2.HealthRequest()
    context = MagicMock(spec=grpc.aio.ServicerContext)

    response = await servicer.Check(request, context)

    assert response.status == "SERVING"


@pytest.mark.asyncio
async def test_health_check_returns_mode():
    """Test that health check returns the configured mode."""
    servicer = HealthServicer()
    request = health_pb2.HealthRequest()
    context = MagicMock(spec=grpc.aio.ServicerContext)

    # Clear the settings cache to pick up environment
    get_settings.cache_clear()

    response = await servicer.Check(request, context)

    assert response.mode == "memory"

    # Cleanup
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_health_check_returns_version():
    """Test that health check returns the package version by default."""
    servicer = HealthServicer()
    request = health_pb2.HealthRequest()
    context = MagicMock(spec=grpc.aio.ServicerContext)

    response = await servicer.Check(request, context)

    expected_version = importlib.metadata.version("petstore-grpc")
    assert response.details.version == expected_version


@pytest.mark.asyncio
async def test_health_check_uses_version_env_override():
    """Test that health check prefers runtime VERSION environment variable."""
    servicer = HealthServicer()
    request = health_pb2.HealthRequest()
    context = MagicMock(spec=grpc.aio.ServicerContext)

    os.environ["VERSION"] = "v0.0.0-beta3"

    response = await servicer.Check(request, context)
    assert response.details.version == "v0.0.0-beta3"

    os.environ.pop("VERSION", None)


@pytest.mark.asyncio
async def test_health_check_returns_build_metadata():
    """Test that health check returns build date and git commit SHA."""
    servicer = HealthServicer()
    request = health_pb2.HealthRequest()
    context = MagicMock(spec=grpc.aio.ServicerContext)

    # Test with default values
    get_settings.cache_clear()
    response = await servicer.Check(request, context)
    assert response.details.build_date == "unknown"
    assert response.details.git_commit_sha == "unknown"

    # Test with custom values
    get_settings.cache_clear()
    os.environ["BUILD_DATE"] = "2024-01-01T00:00:00Z"
    os.environ["GIT_COMMIT_SHA"] = "abc123"

    response = await servicer.Check(request, context)
    assert response.details.build_date == "2024-01-01T00:00:00Z"
    assert response.details.git_commit_sha == "abc123"

    # Cleanup
    get_settings.cache_clear()
    os.environ.pop("BUILD_DATE", None)
    os.environ.pop("GIT_COMMIT_SHA", None)


@pytest.mark.asyncio
async def test_health_check_uses_git_sha_fallback():
    """Test that health check falls back to legacy GIT_SHA environment variable."""
    servicer = HealthServicer()
    request = health_pb2.HealthRequest()
    context = MagicMock(spec=grpc.aio.ServicerContext)

    get_settings.cache_clear()
    os.environ.pop("GIT_COMMIT_SHA", None)
    os.environ["GIT_SHA"] = "legacy-sha"

    response = await servicer.Check(request, context)
    assert response.details.git_commit_sha == "legacy-sha"

    get_settings.cache_clear()
    os.environ.pop("GIT_SHA", None)
