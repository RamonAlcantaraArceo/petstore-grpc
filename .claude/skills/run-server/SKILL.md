# Run Server

This skill starts the petstore-grpc server for local development or testing.

## When to Use

Use this skill to:

- Start the server for manual testing
- Run the server before using grpcurl or other gRPC clients
- Debug server behavior

## Running Locally

### Basic Start

```bash
uv run python -m petstore_grpc
```

Server starts on `localhost:50051` in `dev` mode.

### With Custom Configuration

```bash
# Custom port
PORT=9090 uv run python -m petstore_grpc

# Production mode
STORAGE_MODE=memory uv run python -m petstore_grpc

# Multiple overrides
STORAGE_MODE=cloud PORT=8080 uv run python -m petstore_grpc
```

## Running with Docker

### Using Docker Compose (Recommended)

```bash
# Build and start
docker compose up --build

# Detached mode
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

### With Build Metadata

Inject build timestamp and git commit:

```bash
export BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)
export GIT_COMMIT_SHA=$(git rev-parse HEAD)
docker compose up --build
```

### Direct Docker

```bash
docker build -t petstore-grpc:latest .
docker run -p 50051:50051 petstore-grpc:latest
```

## Testing the Server

Once running, test with grpcurl:

```bash
# Health check
grpcurl -plaintext -d '{}' localhost:50051 petstore.v1.Health/Check
```

Expected response:

```json
{
  "status": "SERVING",
  "mode": "dev",
  "details": {
    "version": "0.1.0",
    "buildDate": "unknown",
    "gitCommitSha": "unknown"
  }
}
```

## Stopping the Server

### Local Process

Press `Ctrl+C` for graceful shutdown (5s grace period).

### Docker Compose

```bash
docker compose down
```

## Configuration Reference

| Variable         | Default   | Description                       |
| ---------------- | --------- | --------------------------------- |
| `PORT`           | `50051`   | gRPC server port                  |
| `STORAGE_MODE`   | `memory`  | Storage backend (memory, postgres, cloud) |
| `BUILD_DATE`     | `unknown` | Build timestamp (Docker only)     |
| `GIT_COMMIT_SHA` | `unknown` | Git commit SHA (Docker only)      |

## Troubleshooting

### Port in Use

```bash
# Check what's using the port
lsof -i :50051

# Use a different port
PORT=50052 uv run python -m petstore_grpc
```

### Import Errors

```bash
# Ensure dependencies are installed
uv sync

# Regenerate proto stubs if needed
bash scripts/gen_protos.sh
```

### Docker Build Fails

```bash
# Clear Docker cache
docker compose build --no-cache

# Check Docker daemon is running
docker ps
```
