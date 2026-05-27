# Copilot Instructions for petstore-grpc

## Commands

```bash
# Install dependencies
uv sync

# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/unit/test_health.py

# Run a single test by name
uv run pytest tests/unit/test_health.py::test_health_check_returns_serving_status

# Lint and format
uv run ruff check .
uv run ruff format .

# Regenerate proto stubs (required after editing .proto files)
bash scripts/gen_protos.sh

# Run server locally
uv run python -m petstore_grpc
```

## Architecture

This service is a **gRPC adapter layer** — it owns no domain logic. Business logic lives in the
external `petstore-api` package (`petstore_core`), pinned in `pyproject.toml` via a git dependency.

```
Browser/gRPC-Web → Envoy (:8080) → Python gRPC server (:50051)
```

**Layer responsibilities:**

- `proto/petstore/v1/` — Protobuf source of truth for the API contract
- `src/petstore_grpc/generated/` — Generated stubs (committed; never edit by hand)
- `src/petstore_grpc/services/` — gRPC servicers that translate proto ↔ `petstore_core` schemas
- `src/petstore_grpc/server.py` — Server bootstrap, `RequestLoggingInterceptor`, graceful shutdown
- `src/petstore_grpc/db.py` — Thin wrapper delegating DB init/session to `petstore_core`
- `src/petstore_grpc/config.py` — `Settings` dataclass (loaded from env, cached via `lru_cache`)

**Storage modes** (controlled by `STORAGE_MODE` env var):

- `memory` (default) — In-process singletons from `services/_memory.py`; state resets on restart
- `postgres` — SQLAlchemy async sessions via `petstore_core`

**gRPC-Web:** Envoy sidecar in `docker-compose.yml` proxies browser requests to the Python server.
TypeScript client stubs are generated on demand via `bash scripts/gen_grpc_web.sh` into `web/grpc/`
(gitignored).

## Key Conventions

**Generated code:** Never edit `src/petstore_grpc/generated/`. To change the API: edit
`proto/petstore/v1/*.proto` → run `bash scripts/gen_protos.sh` → commit generated files. CI fails
(`git diff --exit-code`) if stubs drift from protos.

**Proto field numbers:** Never reuse field numbers after deletion. Use 1–15 for frequently-sent
fields.

**Error mapping:** All servicers catch `petstore_core.errors.DomainError` and delegate to
`services/error_mapping.py::abort_for_domain_error()` to translate to gRPC status codes.

**Settings cache:** `get_settings()` is `lru_cache`-wrapped. Tests that set env vars must call
`get_settings.cache_clear()` before and after to avoid polluting other tests.

**All servicer methods are `async`** — the entire stack uses `grpc.aio`.

**Docstrings:** Google style, enforced by ruff. Line length: 100 characters.

**Version:** Defined once in `src/petstore_grpc/__init__.py`. Runtime reads it via
`importlib.metadata.version("petstore-grpc")`.

**Dependencies:** Add to `pyproject.toml`; run `uv sync`. Never edit `uv.lock` manually.
