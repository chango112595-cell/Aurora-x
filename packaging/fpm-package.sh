#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PKGNAME="auroraos"
VERSION="${1:-1.0.0}"
ARCH="${2:-amd64}"

# Requires fpm installed: gem install --no-document fpm
fpm -s dir -t deb -n "$PKGNAME" -v "$VERSION" --architecture "$ARCH" \
  --prefix /opt/auroraos -C "$ROOT" .
echo "Created package auroraos_${VERSION}_${ARCH}.deb"
