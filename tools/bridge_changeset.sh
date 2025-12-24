#!/usr/bin/env bash
set -euo pipefail
PROMPT="${1:-}"
if [ -z "$PROMPT" ]; then
  echo "usage: tools/bridge_changeset.sh 'your request'"; exit 1
fi
curl -s -X POST "${HOST:-http://127.0.0.1:8000}/api/bridge/nl"   -H 'content-type: application/json'   -d "{"prompt":"${PROMPT}"}" | jq .
