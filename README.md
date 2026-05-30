# Petstore gRPC

A Python gRPC service implementing a pet store API with health check endpoint.

## Shared core dependency

This service consumes framework-agnostic domain and persistence code from `petstore_core` packaged
inside the `petstore-api` dependency. gRPC request/response mapping and gRPC status translation stay
in this repository.

## Features

- **gRPC API** — High-performance RPC framework with Protocol Buffers
- **Health Check** — Service status and build metadata endpoint
- **Modern Python** — Built with Python 3.14, async/await, and type hints
- **Developer Experience** — Fast iteration with `uv`, ruff linting, and comprehensive tests
- **Production Ready** — Multi-stage Docker build, CI/CD, and monitoring hooks

## Quick Start

### Prerequisites

- Python 3.14+
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

# Open grpcui in your browser
# http://localhost:8080/grpcui

# Optional: force banner environment label (otherwise hostname auto-detects)
# GRPCUI_ENV=dev|staging|prod|local docker compose up --build
```

## CLI client

A Typer CLI is available under `cli/` with built-in environment defaults (`local`, `dev`,
`staging`) and transport selection (`grpc`, `rest`).

Both transports stay on the same environment host (for example, DEV uses
`petstore-grpc-dev.fly.dev`).

```bash
# install as a global tool
uv tool install .
petstore-grpc-cli --help
```

```bash
# show resolved endpoints
uv run python -m cli --env dev --transport grpc config
petstore-grpc-cli --env dev --transport grpc config

# check health
uv run python -m cli --env dev --transport grpc health
petstore-grpc-cli --env dev --transport grpc health

# tolerate transient deploy restarts
petstore-grpc-cli --request-timeout 120 --max-retries 8 health

# add/get/list/delete pets
uv run python -m cli --env dev --transport grpc pet add
uv run python -m cli --env dev --transport grpc pet get 1
uv run python -m cli --env dev --transport grpc pet list --status available
uv run python -m cli --env dev --transport grpc pet delete 1
```

All CLI requests/responses are logged to `cli/logs/petstore_cli.log` (override with `--log-file`).

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

## Browser Access via gRPC-Web

The repository ships with an [Envoy](https://www.envoyproxy.io/) sidecar that exposes the
`petstore.v1.Health` service to browsers over gRPC-Web.

### Run the proxy

`docker compose up` starts both the Python gRPC server (`:50051`) and Envoy (`:8080`). Envoy
translates browser gRPC-Web requests into native gRPC and forwards only the `petstore.v1.Health/*`
route to the upstream server.

To enable proxy-level debug logs locally, run:

```bash
LOG_LEVEL=DEBUG docker compose up --build
```

This sets Python server logs to debug and also raises Envoy log level to debug. Envoy access logs
are emitted to container stdout so you can see the HTTP/gRPC forwarding layer for each request.

### Generate the TypeScript client

Requires [`protoc`](https://grpc.io/docs/protoc-installation/) and
[`protoc-gen-grpc-web`](https://github.com/grpc/grpc-web/releases) on `$PATH`.

```bash
bash scripts/gen_grpc_web.sh
```

Output lands in `web/grpc/petstore/v1/` (gitignored — regenerate on demand).

### Call from the browser

```ts
import { checkHealth } from "./web/grpc/HealthClient";

const status = await checkHealth(); // { status, mode, details: {...} }
console.log(status);
```

A minimal demo lives in `web/demo/`:

```bash
cd web
npm install
npm run gen        # generate stubs
npm run build      # bundle demo/main.ts -> demo/main.js
npm run serve      # serve demo at http://localhost:8081
```

With `docker compose up` running, open <http://localhost:8081> and click **Check health**.

## Documentation

Full documentation is available at the
[project docs site](https://ramonalcantaraarceo.github.io/petstore-grpc/).

## Contributing with Claude Code

This repository includes Claude Code agent configurations for enhanced development workflow. See
[CLAUDE.md](CLAUDE.md) for details on using the agent effectively.

## License

MIT
