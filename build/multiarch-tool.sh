#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE_NAME="${1:-auroraos}"
TAG="${2:-latest}"
docker buildx create --use --name aurora-buildx || true
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t "${IMAGE_NAME}:${TAG}" --push -f "$ROOT/docker/Dockerfile.multi" "$ROOT"
