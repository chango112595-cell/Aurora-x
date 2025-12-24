#!/usr/bin/env bash
set -euo pipefail
PROMPT="${1:-}"
if [ -z "$PROMPT" ]; then
  echo "usage: tools/bridge_changeset.sh 'your request'"; exit 1
fi
BASE_URL="${HOST:-http://${AURORA_HOST:-localhost}:${AURORA_NEXUS_PORT:-8000}}"
curl -s -X POST "${BASE_URL}/api/bridge/nl"   -H 'content-type: application/json'   -d "{"prompt":"${PROMPT}"}" | jq .
