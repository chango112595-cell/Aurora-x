#!/usr/bin/env bash
set -euo pipefail
TAG=${1:-}
if [[ -z "$TAG" ]]; then
  echo "Usage: rollback.sh <tag>"
  exit 1
fi
echo "Rollback to $TAG (operator must perform manual checks)"