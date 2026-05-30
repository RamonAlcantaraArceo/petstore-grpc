# CLI

The repository includes a Typer-based CLI under `cli/` to call the API from the terminal.

## Install

```bash
uv tool install .
petstore-grpc-cli --help
```

## Run

```bash
uv run python -m cli --help
petstore-grpc-cli --help
```

## Global options

- `--env`: `local`, `dev`, `staging`
- `--transport`: `grpc`, `rest`
- `--grpc-target`: override gRPC host:port
- `--rest-base-url`: override base URL used for HTTP-framed gRPC calls
- `--log-file`: local request/response log path (default `cli/logs/petstore_cli.log`)

## Commands

```bash
uv run python -m cli --env dev --transport grpc config
uv run python -m cli --env dev --transport grpc health
uv run python -m cli --env dev --transport grpc pet add
uv run python -m cli --env dev --transport grpc pet get 1
uv run python -m cli --env dev --transport grpc pet list --status available --limit 20
uv run python -m cli --env dev --transport grpc pet delete 1

petstore-grpc-cli --env dev --transport grpc config
petstore-grpc-cli --env dev --transport grpc health
petstore-grpc-cli --env dev --transport grpc pet add
petstore-grpc-cli --env dev --transport grpc pet get 1
petstore-grpc-cli --env dev --transport grpc pet list --status available --limit 20
petstore-grpc-cli --env dev --transport grpc pet delete 1
```

## Logging

Each CLI invocation logs structured request/response events to:

```text
cli/logs/petstore_cli.log
```
