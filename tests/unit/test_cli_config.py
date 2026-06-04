"""Unit tests for CLI transport/environment configuration defaults."""

from __future__ import annotations

import json

from cli.main import app
from typer.testing import CliRunner

runner = CliRunner()


def _invoke_config(*args: str) -> dict[str, str]:
    """Run `config` command and return parsed JSON."""
    result = runner.invoke(app, [*args, "config"])
    assert result.exit_code == 0, result.stdout
    return json.loads(result.stdout)


def test_cli_defaults_to_dev_grpc_targets() -> None:
    """Default config should target DEV over native gRPC."""
    output = _invoke_config()

    assert output["environment"] == "dev"
    assert output["transport"] == "grpc"
    assert output["grpc_target"] == "petstore-grpc-dev.fly.dev:443"
    assert output["rest_base_url"] == "https://petstore-grpc-dev.fly.dev"
    assert output["request_timeout"] == 60.0
    assert output["max_retries"] == 5
    assert output["retry_backoff_seconds"] == 1.0


def test_cli_local_rest_points_to_envoy_port() -> None:
    """Local REST transport should default to Envoy listener on :8080."""
    output = _invoke_config("--env", "local", "--transport", "rest")

    assert output["environment"] == "local"
    assert output["transport"] == "rest"
    assert output["grpc_target"] == "localhost:50051"
    assert output["rest_base_url"] == "http://localhost:8080"


def test_cli_allows_override_targets() -> None:
    """CLI should allow explicit endpoint overrides."""
    output = _invoke_config(
        "--env",
        "staging",
        "--transport",
        "grpc",
        "--grpc-target",
        "example.org:7443",
        "--rest-base-url",
        "https://example.org",
    )

    assert output["environment"] == "staging"
    assert output["transport"] == "grpc"
    assert output["grpc_target"] == "example.org:7443"
    assert output["rest_base_url"] == "https://example.org"


def test_cli_allows_override_retry_and_timeout() -> None:
    """CLI should allow retry and timeout overrides."""
    output = _invoke_config(
        "--request-timeout",
        "120",
        "--max-retries",
        "8",
        "--retry-backoff-seconds",
        "2.5",
    )

    assert output["request_timeout"] == 120.0
    assert output["max_retries"] == 8
    assert output["retry_backoff_seconds"] == 2.5
