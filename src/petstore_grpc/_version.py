"""Build-time version source."""

from os import environ


def _normalize_version(raw_version: str) -> str:
    """Return a PEP 440-friendly version for package metadata.

    The runtime image can still expose a tag-style version like ``v1.2.3``, but build metadata
    needs to remain valid for Python packaging.
    """
    if raw_version in {"", "local", "latest"}:
        return "0.0.0+local"
    if raw_version.startswith("v"):
        return raw_version[1:]
    return raw_version


__version__ = _normalize_version(environ.get("VERSION", "local"))
