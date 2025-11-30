#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ARCH="${1:-arm64}" # arm64 or armv7
IMAGE_NAME="yourrepo/aurora-edge:${ARCH}"
docker buildx build --platform linux/${ARCH} -t "$IMAGE_NAME" -f "$ROOT/docker/Dockerfile.edge" "$ROOT" --push
echo "Built edge image $IMAGE_NAME"
