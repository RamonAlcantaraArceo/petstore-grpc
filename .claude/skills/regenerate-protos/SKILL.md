# Regenerate Proto Stubs

This skill regenerates Python gRPC stubs from Protocol Buffer definitions.

## When to Use

Use this skill after:

- Modifying any `.proto` file in `proto/petstore/v1/`
- Adding new `.proto` files
- Pulling changes that include `.proto` modifications

## What It Does

1. Runs `grpc_tools.protoc` to generate `*_pb2.py` and `*_pb2_grpc.py` files
2. Fixes import statements in generated files
3. Places output in `src/petstore_grpc/generated/petstore/v1/`

## Usage

```bash
bash scripts/gen_protos.sh
```

Or invoke via Claude Code skill: `/regenerate-protos`

## After Regenerating

1. **Review changes:** `git diff src/petstore_grpc/generated/`
2. **Update imports:** If you added new services, update import statements in service
   implementations
3. **Run tests:** `uv run pytest` to verify nothing broke
4. **Commit:** Generated files are committed to the repository

## Verification

CI includes a proto drift check that fails if generated files are out of sync:

```bash
bash scripts/gen_protos.sh
git diff --exit-code src/petstore_grpc/generated/
```

If this fails in CI, regenerate locally and commit the changes.

## Example Workflow

After adding a new service definition:

```bash
# 1. Edit proto file
vim proto/petstore/v1/pet.proto

# 2. Regenerate stubs
bash scripts/gen_protos.sh

# 3. Implement servicer
vim src/petstore_grpc/services/pet.py

# 4. Register in server
vim src/petstore_grpc/server.py

# 5. Add tests
vim tests/unit/test_pet.py

# 6. Verify
uv run pytest
```
