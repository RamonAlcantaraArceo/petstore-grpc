# Configuration

## Core environment variables

### Server

- `PORT`: gRPC server port (default `50051`).
- `STORAGE_MODE`: Storage backend (`memory`, `postgres`, `cloud`).
- `LOG_LEVEL`: Python app log level (for example `INFO`, `DEBUG`).

### Envoy (proxy sidecar)

- `ENVOY_LOG_LEVEL`: Envoy log level override (`trace`, `debug`, `info`, ...).
- If `ENVOY_LOG_LEVEL` is not set, Envoy falls back to `LOG_LEVEL`.
- Envoy access logs are emitted to stdout.

## Docker Compose debug logging

Run with debug-level logs for both the Python app and Envoy:

```bash
LOG_LEVEL=DEBUG docker compose up --build
```

If you want to force Envoy to a different level:

```bash
LOG_LEVEL=INFO ENVOY_LOG_LEVEL=debug docker compose up --build
```
