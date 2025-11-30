#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE_NAME="auroraos:latest"
docker buildx create --use --name aurora-buildx || true
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t "$IMAGE_NAME" --load -f "$ROOT/docker/Dockerfile.multi" "$ROOT"
echo "Built $IMAGE_NAME for amd64/arm64/armv7"
