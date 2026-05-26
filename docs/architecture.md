# Architecture

This document describes the high-level architecture and design decisions for petstore-grpc.

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Client                               │
│                     (grpcurl, app)                          │
└─────────────────────────┬───────────────────────────────────┘
                          │ gRPC / HTTP/2
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   petstore-grpc Server                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  server.py (grpc.aio.server)                          │  │
│  │    • Service registration                             │  │
│  │    • Port binding                                     │  │
│  │    • Graceful shutdown                                │  │
│  └───────────────────────┬───────────────────────────────┘  │
│                          │                                   │
│  ┌───────────────────────▼───────────────────────────────┐  │
│  │  services/health.py (HealthServicer)                  │  │
│  │    • Health/Check RPC                                 │  │
│  │    • Build metadata aggregation                       │  │
│  └───────────────────────┬───────────────────────────────┘  │
│                          │                                   │
│  ┌───────────────────────▼───────────────────────────────┐  │
│  │  config.py (Settings)                                 │  │
│  │    • Environment variable loading                     │  │
│  │    • Singleton cached settings                        │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Proto Definitions (`proto/petstore/v1/`)

Protocol Buffer schemas define the API contract:

- **health.proto** — Health check service and messages

Generated Python stubs are committed to the repository in `src/petstore_grpc/generated/`. This
simplifies CI and eliminates build-time codegen.

### 2. Server Bootstrap (`server.py`)

The main server lifecycle manager:

- Creates `grpc.aio.server()` for async-first design
- Registers all servicers (currently `HealthServicer`)
- Binds to `0.0.0.0:${PORT}` (default 50051)
- Handles SIGTERM/SIGINT for graceful shutdown with 5s grace period

### 3. Health Service (`services/health.py`)

Implements the `Health/Check` RPC:

**Response fields:**

- `status` — Always `"SERVING"` (future: readiness checks)
- `mode` — Runtime mode from `MODE` env var (dev, prod, staging)
- `details.version` — Package version via `importlib.metadata`
- `details.build_date` — Build timestamp (injected by Docker, defaults to "unknown")
- `details.git_commit_sha` — Git commit SHA (injected by Docker, defaults to "unknown")

### 4. Configuration (`config.py`)

Environment variable loader with caching:

- `Settings` dataclass (frozen) holds all config
- `get_settings()` uses `@lru_cache` for singleton pattern
- Tests can clear cache to inject custom env vars

### 5. Entry Point (`__main__.py`)

Simple entry point for `python -m petstore_grpc`:

- Configures logging
- Calls `asyncio.run(serve())`

## Design Decisions

### Async-First with grpc.aio

All server and servicer code uses `async`/`await`:

- **Benefits:** Non-blocking I/O, efficient concurrency, native asyncio integration
- **Trade-offs:** Slightly more complex than sync code, but better scalability

### Generated Stubs Committed

Proto-generated Python files are checked into version control:

- **Pros:** No codegen in CI/Docker, faster builds, explicit diffs
- **Cons:** Manual regeneration required after `.proto` changes
- **Mitigation:** CI job checks for drift (`git diff --exit-code`)

### Version from `__init__.py`

Hatchling reads `__version__` from `src/petstore_grpc/__init__.py`:

- Single source of truth
- Simple to update (just edit the string)
- Runtime lookup via `importlib.metadata.version("petstore-grpc")`

### Build Metadata via Docker ARG/ENV

Build date and git commit are injected at Docker build time:

- `ARG BUILD_DATE` / `ENV BUILD_DATE`
- `ARG GIT_COMMIT_SHA` / `ENV GIT_COMMIT_SHA`
- Defaults to `"unknown"` for local dev (no Docker)

### uv for Dependency Management

Uses the fast `uv` package manager:

- `pyproject.toml` + `uv.lock` for reproducible installs
- `uv sync` instead of `pip install`
- Faster than pip, especially in Docker

### Ruff-Only Linting

Consolidates formatting and linting into a single tool:

- Replaces black, isort, flake8, and more
- Google-style docstrings enforced via pydocstyle rules
- Generated code excluded via `per-file-ignores`

## Directory Structure

```
petstore-grpc/
├── src/petstore_grpc/         # Source code
│   ├── __init__.py            # Package + version
│   ├── __main__.py            # Entry point
│   ├── server.py              # gRPC server
│   ├── config.py              # Environment config
│   ├── services/              # RPC implementations
│   │   └── health.py
│   └── generated/             # Proto stubs (committed)
│       └── petstore/v1/
├── tests/                     # Test suite
│   ├── conftest.py            # Shared fixtures
│   ├── unit/                  # Fast, isolated tests
│   └── integration/           # Full gRPC tests
├── proto/                     # Proto definitions
│   └── petstore/v1/
├── scripts/                   # Dev tooling
│   └── gen_protos.sh
├── docs/                      # Documentation (mkdocs)
├── .github/workflows/         # CI/CD
├── .claude/                   # Agent configurations
├── Dockerfile                 # Multi-stage build
├── docker-compose.yml         # Local orchestration
└── pyproject.toml             # Python project metadata
```

## Future Enhancements

### Readiness Checks

Currently `status` is hard-coded to `"SERVING"`. Future work:

- Add dependency health checks (database, external APIs)
- Return `"NOT_SERVING"` if dependencies are unavailable

### Observability

Potential integrations:

- OpenTelemetry for distributed tracing
- Prometheus metrics export
- Structured logging (JSON) for production

### Additional Services

The architecture supports adding more gRPC services:

1. Define `.proto` in `proto/petstore/v1/`
2. Regenerate stubs via `scripts/gen_protos.sh`
3. Implement servicer in `src/petstore_grpc/services/`
4. Register in `server.py`
5. Add tests in `tests/`

## Security Considerations

### Non-Root Container

Dockerfile creates and runs as user `appuser` (UID 1000):

```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

### No Secrets in Env Vars

Build metadata (`BUILD_DATE`, `GIT_COMMIT_SHA`) is non-sensitive. For secrets:

- Use Docker secrets or Kubernetes secrets
- Never log or expose in health responses

### Input Validation

gRPC automatically validates message types via protobuf. For custom validation:

- Add checks in servicer methods
- Return `grpc.StatusCode.INVALID_ARGUMENT` for bad input
