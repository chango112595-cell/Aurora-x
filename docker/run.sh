#!/usr/bin/env bash
set -euo pipefail
IMAGE="${1:-auroraos:latest}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

docker run -d --name aurora \
  -p 5000:5000 -p 9701:9701 -p 9702:9702 \
  -v "$ROOT":/app \
  --restart unless-stopped \
  "$IMAGE"
echo "Aurora container started (name=aurora)"
