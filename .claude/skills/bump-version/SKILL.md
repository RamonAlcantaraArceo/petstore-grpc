# Bump Version

This skill updates the package version and creates a git tag.

## When to Use

Use this skill when:

- Preparing a new release
- Publishing a new version to PyPI (future)
- Creating a changelog entry

## How Versioning Works

- Version is injected at image build/deploy time through `VERSION`
- Git tags should match the released image tag (e.g., `v0.1.0`)
- Runtime code reads `VERSION` first and falls back to package metadata outside containers

## Steps to Bump Version

### 1. Update Changelog (if present)

```markdown
# In CHANGELOG.md

## [0.2.0] - 2024-XX-XX

### Added

- New feature X

### Fixed

- Bug Y
```

### 2. Commit Changes

```bash
git add CHANGELOG.md
git commit -m "Bump version to 0.2.0"
```

### 3. Create Git Tag

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

# Commit and tag
git add CHANGELOG.md
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

After bumping, verify the deployed image reports the new tag:

```bash
VERSION=v0.2.0 docker compose build
VERSION=v0.2.0 docker compose up -d
grpcurl -plaintext -d '{}' localhost:50051 petstore.v1.Health/Check
```

Expected output: `details.version == "v0.2.0"`

## Release Checklist

1. [ ] Update `CHANGELOG.md` (if present)
1. [ ] Run tests: `uv run pytest`
1. [ ] Commit changes: `git commit -m "Release vX.Y.Z"`
1. [ ] Create tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
1. [ ] Build and deploy with `VERSION=vX.Y.Z`
1. [ ] Push: `git push origin main --tags`
1. [ ] Verify CI passes
