#!/usr/bin/env bash
FILE="$1"
if [[ -z "$FILE" ]]; then
  echo "usage: $0 path/to/update.tar.gz"
  exit 1
fi
gpg --verify "${FILE}.asc" "$FILE" || { echo "signature invalid"; exit 2; }
sha256sum -c "${FILE}.sha256" || { echo "checksum mismatch"; exit 3; }
echo "signature and checksum OK"
