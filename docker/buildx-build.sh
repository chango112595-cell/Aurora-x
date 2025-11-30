#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE="yourrepo/auroraos"
TAG="${1:-latest}"
docker buildx create --use --name aurora-buildx || true
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t "$IMAGE:$TAG" --push -f "$ROOT/docker/Dockerfile.multi" "$ROOT"
echo "Multi-arch image pushed: $IMAGE:$TAG"
