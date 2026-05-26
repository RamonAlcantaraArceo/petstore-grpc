#!/usr/bin/env bash
set -euo pipefail

# Navigate to repo root
cd "$(dirname "$0")/.."

# Create generated directory if it doesn't exist
mkdir -p src/petstore_grpc/generated

# Generate Python stubs for all service protos
uv run python -m grpc_tools.protoc \
  --proto_path=proto \
  --python_out=src/petstore_grpc/generated \
  --grpc_python_out=src/petstore_grpc/generated \
  proto/petstore/v1/common.proto \
  proto/petstore/v1/health.proto \
  proto/petstore/v1/pet.proto \
  proto/petstore/v1/store.proto \
  proto/petstore/v1/user.proto

# Fix imports in generated files (grpc_tools generates absolute imports that need adjustment)
# Replace "from petstore.v1 import foo_pb2" with "from . import foo_pb2" in all generated files
SED_PATTERN='s/^from petstore\.v1 import \(.*\)_pb2 as/from . import \1_pb2 as/g'
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS sed
  find src/petstore_grpc/generated -name "*_pb2.py" -o -name "*_pb2_grpc.py" \
    | xargs -I{} sed -i '' "$SED_PATTERN" {}
else
  # GNU sed
  find src/petstore_grpc/generated -name "*_pb2.py" -o -name "*_pb2_grpc.py" \
    | xargs -I{} sed -i "$SED_PATTERN" {}
fi

uv run ruff format src/petstore_grpc/generated
uv run ruff check src/petstore_grpc/generated --fix --unsafe-fixes

echo "✓ Proto stubs generated successfully"
