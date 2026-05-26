"""Entry point for running petstore-grpc as a module."""

import asyncio
import logging

from petstore_grpc.server import serve


def main() -> None:
    """Main entry point for the gRPC server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    asyncio.run(serve())


if __name__ == "__main__":
    main()
