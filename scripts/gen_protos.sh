#!/usr/bin/env bash
set -euo pipefail

# Navigate to repo root
cd "$(dirname "$0")/.."

# Create generated directory if it doesn't exist
mkdir -p src/petstore_grpc/generated

# Generate Python stubs
python -m grpc_tools.protoc \
  --proto_path=proto \
  --python_out=src/petstore_grpc/generated \
  --grpc_python_out=src/petstore_grpc/generated \
  proto/petstore/v1/health.proto

# Fix imports in generated files (grpc_tools generates relative imports that need adjustment)
# Replace "import health_pb2" with "from . import health_pb2" in *_grpc.py files
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS sed
  find src/petstore_grpc/generated -name "*_pb2_grpc.py" -exec sed -i '' 's/^import \(.*\)_pb2 as/from . import \1_pb2 as/g' {} \;
else
  # GNU sed
  find src/petstore_grpc/generated -name "*_pb2_grpc.py" -exec sed -i 's/^import \(.*\)_pb2 as/from . import \1_pb2 as/g' {} \;
fi

echo "✓ Proto stubs generated successfully"
