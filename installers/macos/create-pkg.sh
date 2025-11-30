#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PKG_ID="com.aurora.os"
INSTALL_LOCATION="/Applications/AuroraOS"
BUILD_ROOT="${ROOT}/pkgbuild_root"
rm -rf "$BUILD_ROOT"
mkdir -p "$BUILD_ROOT/${INSTALL_LOCATION}"
rsync -av --exclude='.git' "${ROOT}/" "$BUILD_ROOT/${INSTALL_LOCATION}/"
pkgbuild --root "$BUILD_ROOT" --identifier "$PKG_ID" --version "1.0.0" --install-location "/" "${ROOT}/AuroraOS.pkg"

echo "Created ${ROOT}/AuroraOS.pkg"
