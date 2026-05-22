# Claude Code Agent Guide for petstore-grpc

This document provides guidance for Claude Code when working on the petstore-grpc repository.

## Project Overview

**petstore-grpc** is a Python gRPC service implementing a pet store API. The current implementation
includes a Health endpoint that returns service status and build metadata.

## Repository Structure

```
petstore-grpc/
├── src/petstore_grpc/         # Source code
│   ├── services/              # gRPC service implementations
│   └── generated/             # Generated proto stubs (COMMITTED)
├── tests/                     # pytest test suite
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
├── proto/petstore/v1/         # Protocol Buffer definitions
├── scripts/                   # Development scripts
│   └── gen_protos.sh          # Proto stub generator
├── docs/                      # MkDocs documentation
└── .claude/                   # Claude agent configuration
```

## Common Commands

### Development Workflow

```bash
# Install dependencies
uv sync

# Run the server locally
uv run python -m petstore_grpc

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov-report=html

# Lint and format
uv run ruff check .
uv run ruff format .

# Check markdown formatting
npx prettier --check "**/*.md"
npx prettier --write "**/*.md"

# Regenerate proto stubs (after modifying .proto files)
bash scripts/gen_protos.sh

# Build and run with Docker
docker compose up --build

# Build docs locally
uv run mkdocs serve
```

### Testing the Server

```bash
# Install grpcurl (if needed)
# macOS: brew install grpcurl
# Linux: https://github.com/fullstorydev/grpcurl/releases

# Test health endpoint
grpcurl -plaintext -d '{}' localhost:50051 petstore.v1.Health/Check
```

## Code Conventions

### Python Style

- **Line length:** 100 characters
- **Docstrings:** Google style (enforced by ruff)
- **Imports:** Sorted by ruff (I rule)
- **Formatting:** ruff format (replaces black)
- **Type hints:** Use where beneficial, not mandatory everywhere

### Example Docstring

```python
def my_function(arg1: str, arg2: int) -> bool:
    """Short one-line summary.

    Longer description if needed. Explain the purpose and behavior.

    Args:
        arg1: Description of first argument.
        arg2: Description of second argument.

    Returns:
        Description of return value.

    Raises:
        ValueError: When input is invalid.
    """
```

### Async Code

All gRPC servicers and server code use async/await:

```python
async def Check(
    self,
    request: health_pb2.HealthRequest,
    context: grpc.aio.ServicerContext,
) -> health_pb2.HealthResponse:
    """Handle health check request."""
    # Implementation
```

### Testing Conventions

- Unit tests: Mock external dependencies, test logic in isolation
- Integration tests: Full gRPC client/server interaction
- Use pytest fixtures from `conftest.py` for shared setup
- Mark async tests with `@pytest.mark.asyncio`

## Important Rules

### Generated Code

**NEVER edit files in `src/petstore_grpc/generated/` by hand!**

These files are generated from `.proto` definitions. To update:

1. Edit the `.proto` file in `proto/petstore/v1/`
2. Run `bash scripts/gen_protos.sh`
3. Commit the updated generated files

The CI pipeline verifies stubs are up-to-date via `git diff --exit-code`.

### Proto Definitions

When modifying `.proto` files:

- Never reuse field numbers (even after deletion)
- Use semantic field numbering (1-15 for frequent fields)
- Document fields with comments
- Consider backward compatibility

After changes, always:

1. Regenerate stubs: `bash scripts/gen_protos.sh`
2. Update affected service implementations
3. Update tests
4. Run full test suite

### Versioning

Version is defined in `src/petstore_grpc/__init__.py`:

```python
__version__ = "0.1.0"
```

Hatchling reads this at build time. Runtime code accesses it via:

```python
import importlib.metadata
version = importlib.metadata.version("petstore-grpc")
```

To bump version: Edit `__version__` in `__init__.py` and create a git tag.

### Dependency Management

- **Never edit `uv.lock` manually**
- Add dependencies to `pyproject.toml` under `dependencies` or `dev-dependencies`
- Run `uv sync` to update the lockfile
- Use `uv add <package>` for convenience

### Docker Build Metadata

Build date and git commit SHA are injected via Docker build args:

```bash
docker compose build \
  --build-arg BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --build-arg GIT_COMMIT_SHA=$(git rev-parse HEAD)
```

These default to `"unknown"` when running locally without Docker.

## Skills

Claude Code has access to specialized skills for common tasks:

- **/regenerate-protos** — Regenerate proto stubs after `.proto` changes
- **/run-server** — Start the server locally or with Docker
- **/bump-version** — Update version and create git tag

Invoke these via the skill name when appropriate.

## Agents

- **proto-reviewer** — Subagent for reviewing `.proto` file changes for breaking changes,
  field reuse, and naming conventions

## Debugging

### Import Errors

If you see import errors for generated proto files:

```bash
# Regenerate stubs
bash scripts/gen_protos.sh

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
uv sync
```

### Server Won't Start

Check for:

- Port conflicts (default 50051)
- Missing dependencies (`uv sync`)
- Environment variable issues (`MODE`, `PORT`)

### Tests Failing

Common causes:

- Stale `__pycache__` — delete and retry
- Missing dependencies — run `uv sync`
- Environment state — tests should be isolated, check for leaked state

## CI/CD

GitHub Actions workflows:

- **ci.yml** — Runs on push/PR: lint, test, proto drift check
- **docs.yml** — Deploys to GitHub Pages on docs changes to main

All checks must pass before merging to main.

## Documentation

- Docs are built with MkDocs (Material theme)
- Markdown files in `docs/`
- Auto-deployed to GitHub Pages on changes to `main`
- Local preview: `uv run mkdocs serve`

When adding new pages, update `nav` section in `mkdocs.yml`.

## Tips for Claude Code

1. **Read before editing:** Always read existing code before making changes
2. **Run tests:** After code changes, run `uv run pytest` to verify
3. **Format on save:** The hooks auto-format, but you can run `uv run ruff format .`
4. **Check proto drift:** After regenerating protos, ensure CI passes
5. **Update docs:** Keep documentation in sync with code changes
