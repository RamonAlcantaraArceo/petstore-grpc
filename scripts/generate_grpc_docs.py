#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTO_DIR = ROOT / "proto" / "petstore" / "v1"
OUTPUT_DIR = ROOT / "docs" / "grpc"
OUTPUT_FILE = "grpc.md"

def main():
    # Validate proto directory
    if not PROTO_DIR.exists():
        print(f"❌ Proto directory not found: {PROTO_DIR}")
        sys.exit(1)

    # Collect all .proto files
    proto_files = list(PROTO_DIR.glob("*.proto"))
    if not proto_files:
        print(f"❌ No .proto files found in {PROTO_DIR}")
        sys.exit(1)

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Build docker command
    docker_cmd = [
        "docker", "run", "--rm",
        "--platform", "linux/amd64",
        "-v", f"{ROOT}:/workspace",
        "pseudomuto/protoc-gen-doc",
        "--doc_opt=markdown," + OUTPUT_FILE,
        f"--doc_out=/workspace/{OUTPUT_DIR.relative_to(ROOT)}",
        "-I", "/workspace/proto",
    ]

    # Append proto files with /workspace prefix
    docker_cmd.extend([f"/workspace/{p.relative_to(ROOT)}" for p in proto_files])

    print("🚀 Running protoc-gen-doc...")
    print("📁 Proto files:")
    for p in proto_files:
        print(f"   - {p}")

    try:
        subprocess.run(docker_cmd, check=True)
        print(f"\n✅ Documentation generated at: {OUTPUT_DIR / OUTPUT_FILE}")
    except subprocess.CalledProcessError as e:
        print("\n❌ Failed to generate documentation")
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
