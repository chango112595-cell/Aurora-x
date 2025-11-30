#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NAME="auroraos"
VERSION="${1:-1.0.0}"
ARCH="${2:-amd64}"

if ! command -v fpm >/dev/null 2>&1; then
  echo "Install fpm: gem install --no-document fpm"
  exit 1
fi

fpm -s dir -t deb -n "$NAME" -v "$VERSION" --architecture "$ARCH" \
  --prefix /opt/auroraos -C "$ROOT" .
echo "Created ${NAME}_${VERSION}_${ARCH}.deb"
