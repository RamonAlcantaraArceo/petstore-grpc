"""Entry point for running petstore-grpc as a module."""

import asyncio
import logging
import os

from petstore_grpc.server import serve


def main() -> None:
    """Main entry point for the gRPC server."""
    log_level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    logging.getLogger(__name__).info("Logging initialized at level=%s", log_level_name)
    asyncio.run(serve())


if __name__ == "__main__":
    main()
