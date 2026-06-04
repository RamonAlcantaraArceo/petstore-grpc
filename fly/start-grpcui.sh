#!/bin/sh

set -eu

ASSET_DIR="/app/grpcui-assets"
mkdir -p "${ASSET_DIR}"

override="${GRPCUI_ENV:-}"
escaped_override=$(printf '%s' "${override}" | sed 's/\\/\\\\/g; s/"/\\"/g')

cat > "${ASSET_DIR}/env.js" <<EOF
window.__PETSTORE_GRPCUI_ENV_OVERRIDE__ = "${escaped_override}";
EOF

exec /usr/local/bin/grpcui \
  -plaintext \
  -connect-fail-fast=false \
  -port 8081 \
  -base-path /grpcui \
  -also-serve "${ASSET_DIR}" \
  -extra-css "${ASSET_DIR}/banner.css" \
  -extra-js "${ASSET_DIR}/env.js" \
  -extra-js "${ASSET_DIR}/banner.js" \
  127.0.0.1:50051
