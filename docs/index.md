# Petstore gRPC

A Python gRPC service implementing a pet store API with health check endpoint.

## Features

- **gRPC API** — High-performance RPC framework with Protocol Buffers
- **Health Check** — Service status and build metadata endpoint
- **Modern Python** — Built with Python 3.12, async/await, and type hints
- **Developer Experience** — Fast iteration with `uv`, ruff linting, and comprehensive tests
- **Production Ready** — Multi-stage Docker build, CI/CD, and monitoring hooks

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/RamonAlcantaraArceo/petstore-grpc.git
cd petstore-grpc

# Install dependencies
uv sync
```

### Running Locally

```bash
# Start the server
uv run python -m petstore_grpc

# In another terminal, test the health endpoint
grpcurl -plaintext -d '{}' localhost:50051 petstore.v1.Health/Check
```

### Running with Docker

```bash
# Build and run with docker compose
docker compose up --build

# Test the endpoint
grpcurl -plaintext -d '{}' localhost:50051 petstore.v1.Health/Check
```

## Development

### Running Tests

```bash
uv run pytest
```

### Linting and Formatting

```bash
# Check formatting
uv run ruff check .
uv run ruff format --check .

# Auto-fix issues
uv run ruff check --fix .
uv run ruff format .
```

### Regenerating Proto Stubs

After modifying `.proto` files:

```bash
bash scripts/gen_protos.sh
```

## Documentation

Full documentation is available at the
[project docs site](https://ramonalcantaraarceo.github.io/petstore-grpc/).

## Contributing with Claude Code

This repository includes Claude Code agent configurations for enhanced development workflow. See
`CLAUDE.md` in the repository for details on using the agent effectively.

## License

MIT
