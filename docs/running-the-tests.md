# Running the Tests

This guide explains how to run the test suite and interpret results.

## Running All Tests

```bash
uv run pytest
```

This runs all unit and integration tests with coverage reporting.

## Running Specific Tests

### By Directory

```bash
# Unit tests only
uv run pytest tests/unit/

# Integration tests only
uv run pytest tests/integration/
```

### By File

```bash
uv run pytest tests/unit/test_health.py
```

### By Test Name

```bash
uv run pytest tests/unit/test_health.py::test_health_check_returns_serving_status
```

## Coverage Reports

### Terminal Output

Coverage is displayed in the terminal after tests complete:

```bash
uv run pytest
```

### HTML Report

Generate a detailed HTML coverage report:

```bash
uv run pytest --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Coverage Requirements

The project enforces coverage via pytest configuration in `pyproject.toml`. To adjust:

```toml
[tool.pytest.ini_options]
addopts = "-ra --strict-markers --cov=petstore_grpc --cov-fail-under=80"
```

## Test Organization

### Unit Tests (`tests/unit/`)

Fast, isolated tests that mock external dependencies:

- `test_health.py` — Health servicer logic with mocked gRPC context

### Integration Tests (`tests/integration/`)

End-to-end tests with real gRPC channels:

- `test_server_startup.py` — Full server lifecycle and RPC invocation

### Fixtures (`tests/conftest.py`)

Shared test infrastructure:

- `grpc_server` — In-process server on ephemeral port
- `grpc_channel` — Client channel connected to test server

## Writing Tests

### Unit Test Example

```python
import pytest
from unittest.mock import MagicMock
from petstore_grpc.services.health import HealthServicer
from petstore_grpc.generated.petstore.v1 import health_pb2

@pytest.mark.asyncio
async def test_my_feature():
    servicer = HealthServicer()
    request = health_pb2.HealthRequest()
    context = MagicMock()

    response = await servicer.Check(request, context)

    assert response.status == "SERVING"
```

### Integration Test Example

```python
import pytest
from petstore_grpc.generated.petstore.v1 import health_pb2, health_pb2_grpc

@pytest.mark.asyncio
async def test_end_to_end(grpc_channel):
    stub = health_pb2_grpc.HealthStub(grpc_channel)
    request = health_pb2.HealthRequest()

    response = await stub.Check(request)

    assert response.status == "SERVING"
```

## Continuous Integration

Tests run automatically on every push and pull request via GitHub Actions:

- **Lint** — Ruff check and format validation
- **Markdown** — Prettier formatting check
- **Test** — Full pytest suite with coverage
- **Proto Check** — Verify generated stubs are up to date

See `.github/workflows/ci.yml` in the repository for the full CI pipeline.

## Troubleshooting

### Async Tests Failing

Ensure `pytest-asyncio` is installed and configured:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

### Import Errors

Clear Python cache and reinstall:

```bash
find . -type d -name __pycache__ -exec rm -r {} +
uv sync
```

### Port Conflicts

Integration tests use ephemeral ports, so conflicts are rare. If you see port errors, ensure no
other tests are running concurrently.
