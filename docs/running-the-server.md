# Running the Server

This guide covers different ways to run the petstore-grpc server.

## Local Development

### Using uv (Recommended)

The fastest way to run the server locally:

```bash
uv run python -m petstore_grpc
```

This starts the server on `localhost:50051` in development mode.

### Configuration

The server reads configuration from environment variables:

| Variable         | Default   | Description                       |
| ---------------- | --------- | --------------------------------- |
| `PORT`           | `50051`   | gRPC server port                  |
| `STORAGE_MODE`   | `memory`  | Storage backend (memory, postgres, cloud) |
| `BUILD_DATE`     | `unknown` | Build timestamp (set by Docker)   |
| `GIT_COMMIT_SHA` | `unknown` | Git commit SHA (set by Docker)    |

Example with custom configuration:

```bash
STORAGE_MODE=cloud PORT=9090 uv run python -m petstore_grpc
```

## Docker

### Using Docker Compose

The recommended way to run in a containerized environment:

```bash
# Build and start
docker compose up --build

# Run in detached mode
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

### Building with Build Metadata

To inject build metadata (timestamp and git commit):

```bash
docker compose build \
  --build-arg BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --build-arg GIT_COMMIT_SHA=$(git rev-parse HEAD)

docker compose up
```

### Using Docker Directly

```bash
# Build
docker build -t petstore-grpc:latest .

# Run
docker run -p 50051:50051 petstore-grpc:latest
```

## Testing the Server

Once the server is running, test the Health endpoint using `grpcurl`:

```bash
# Install grpcurl if needed
# macOS: brew install grpcurl
# Linux: https://github.com/fullstorydev/grpcurl/releases

# Call the health check
grpcurl -plaintext -d '{}' localhost:50051 petstore.v1.Health/Check
```

Expected response:

```json
{
  "status": "SERVING",
  "mode": "memory",
  "details": {
    "version": "0.0.0-local",
    "buildDate": "today",
    "gitCommitSha": "dead-beef"
  }
}
```

## Troubleshooting

### Port Already in Use

If port 50051 is already in use, change it via the `PORT` environment variable:

```bash
PORT=50052 uv run python -m petstore_grpc
```

### Import Errors

If you see import errors, ensure dependencies are installed:

```bash
uv sync
```

### Proto Stubs Missing

If you see errors about missing `health_pb2` modules, regenerate the stubs:

```bash
bash scripts/gen_protos.sh
```
