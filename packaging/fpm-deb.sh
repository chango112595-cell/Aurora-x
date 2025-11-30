#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PKG="auroraos"
VER="${1:-1.0.0}"
ARCH="${2:-amd64}"

# requires fpm: gem install --no-document fpm
fpm -s dir -t deb -n "$PKG" -v "$VER" --architecture "$ARCH" --prefix /opt/auroraos -C "$ROOT" .
echo "DEB/RPM package created (use fpm -t rpm to create rpm)."
