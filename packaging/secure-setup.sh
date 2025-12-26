#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOKEN="${1:-$(openssl rand -hex 24)}"
echo "$TOKEN" > "$ROOT/.aurora/api.token"
echo "Created API token and stored in .aurora/api.token"

# create TLS cert for local dev (mkcert if available)
if command -v mkcert >/dev/null 2>&1; then
  mkcert -install
  mkcert -key-file "$ROOT/.aurora/127.0.0.1-key.pem" -cert-file "$ROOT/.aurora/127.0.0.1-cert.pem" "127.0.0.1" "127.0.0.1"
  echo "Created dev certs at ./.aurora/"
else
  echo "mkcert not installed; to create TLS certs run: mkcert -install && mkcert 127.0.0.1 127.0.0.1"
fi
