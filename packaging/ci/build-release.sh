#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TAG=${1:-"v1.0.0"}
echo "Building release $TAG..."

# 1) Build docker multi-arch
bash docker/buildx-build.sh

# 2) Build deb/rpm
bash installers/linux/create-deb.sh "$TAG" amd64
bash installers/linux/create-rpm.sh "$TAG" x86_64

# 3) Build mac pkg (local)
bash installers/macos/create-pkg.sh

# 4) Build windows msi (if WiX installed)
# powershell -File installers/windows/create-msi.ps1

echo "Artifacts generated. Collect files in packaging/artifacts/"
