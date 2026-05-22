# Bump Version

This skill updates the package version and creates a git tag.

## When to Use

Use this skill when:

- Preparing a new release
- Publishing a new version to PyPI (future)
- Creating a changelog entry

## How Versioning Works

Version is stored in `src/petstore_grpc/__init__.py`:

```python
__version__ = "0.1.0"
```

- Hatchling reads this at build time
- Runtime code accesses via `importlib.metadata.version("petstore-grpc")`
- Git tags should match the version (e.g., `v0.1.0`)

## Steps to Bump Version

### 1. Edit Version String

```python
# In src/petstore_grpc/__init__.py
__version__ = "0.2.0"  # Increment as needed
```

### 2. Update Changelog (if present)

```markdown
# In CHANGELOG.md
## [0.2.0] - 2024-XX-XX

### Added

- New feature X

### Fixed

- Bug Y
```

### 3. Commit Changes

```bash
git add src/petstore_grpc/__init__.py CHANGELOG.md
git commit -m "Bump version to 0.2.0"
```

### 4. Create Git Tag

```bash
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin main --tags
```

## Semantic Versioning

Follow [SemVer](https://semver.org/) conventions:

- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.2.0): New features, backward-compatible
- **PATCH** (0.1.1): Bug fixes, backward-compatible

Examples:

- `0.1.0` → `0.1.1`: Bug fix
- `0.1.1` → `0.2.0`: New endpoint added
- `0.2.0` → `1.0.0`: Breaking API change

## Automated Script (Future)

This can be automated with a script:

```bash
#!/usr/bin/env bash
# scripts/bump_version.sh

NEW_VERSION=$1

# Update __init__.py
sed -i "s/__version__ = .*/__version__ = \"${NEW_VERSION}\"/" \
  src/petstore_grpc/__init__.py

# Commit and tag
git add src/petstore_grpc/__init__.py
git commit -m "Bump version to ${NEW_VERSION}"
git tag -a "v${NEW_VERSION}" -m "Release v${NEW_VERSION}"

echo "✓ Version bumped to ${NEW_VERSION}"
echo "Run: git push origin main --tags"
```

Usage:

```bash
bash scripts/bump_version.sh 0.2.0
```

## Verification

After bumping, verify the version is correct:

```bash
# Install and check
uv sync
uv run python -c "import importlib.metadata; print(importlib.metadata.version('petstore-grpc'))"
```

Expected output: `0.2.0`

## Release Checklist

1. [ ] Update version in `src/petstore_grpc/__init__.py`
2. [ ] Update `CHANGELOG.md` (if present)
3. [ ] Run tests: `uv run pytest`
4. [ ] Commit changes: `git commit -m "Bump version to X.Y.Z"`
5. [ ] Create tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
6. [ ] Push: `git push origin main --tags`
7. [ ] Verify CI passes
8. [ ] (Future) Publish to PyPI: `uv build && uv publish`
