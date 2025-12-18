#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PKG_ID="com.aurora.os"
PKG_VERSION="${1:-1.0.0}"
TMP="$(mktemp -d)"
mkdir -p "$TMP/Applications/AuroraOS"
cp -r "$ROOT"/* "$TMP/Applications/AuroraOS/"
pkgbuild --root "$TMP/Applications" --identifier "$PKG_ID" --version "$PKG_VERSION" "AuroraOS-$PKG_VERSION.pkg"
echo "PKG created: AuroraOS-$PKG_VERSION.pkg"
