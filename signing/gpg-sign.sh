#!/usr/bin/env bash
set -euo pipefail
FILE="$1"
if [[ -z "$FILE" ]]; then
  echo "usage: $0 path/to/update.tar.gz"
  exit 1
fi
gpg --armor --detach-sign "$FILE"
sha256sum "$FILE" > "${FILE}.sha256"
echo "Signed: ${FILE}.asc and ${FILE}.sha256"
