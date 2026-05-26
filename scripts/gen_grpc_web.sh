#!/usr/bin/env bash
# Generate gRPC-Web TypeScript client stubs for browser consumption.
#
# Requirements:
#   - protoc            (https://grpc.io/docs/protoc-installation/)
#   - protoc-gen-grpc-web (https://github.com/grpc/grpc-web/releases)
#
# Both must be available on $PATH.
set -euo pipefail

cd "$(dirname "$0")/.."

OUT_DIR="web/grpc"
mkdir -p "${OUT_DIR}"

if ! command -v protoc >/dev/null 2>&1; then
  echo "error: protoc not found on PATH" >&2
  exit 1
fi

# Prefer local npm-installed plugin binaries by adding common node_modules/.bin
# directories to PATH so plugins installed via npm are discoverable by protoc.
for p in "./web/node_modules/.bin" "./node_modules/.bin"; do
  if [ -d "$p" ]; then
    PATH="$(pwd)/$p:$PATH"
  fi
done
export PATH

if ! command -v protoc-gen-grpc-web >/dev/null 2>&1; then
  echo "error: protoc-gen-grpc-web not found on PATH" >&2
  echo "  Install via npm (recommended):" >&2
  echo "    cd web && npm install --save-dev @protocolbuffers/protoc-gen-js" >&2
  echo "  Or download the official binary: https://github.com/grpc/grpc-web/releases" >&2
  exit 1
fi

protoc \
  -I proto \
  --js_out=import_style=commonjs:"${OUT_DIR}" \
  --grpc-web_out=import_style=typescript,mode=grpcweb:"${OUT_DIR}" \
  proto/petstore/v1/health.proto

echo "✓ gRPC-Web client generated into ${OUT_DIR}/petstore/v1/"
