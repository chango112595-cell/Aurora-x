#!/usr/bin/env bash
# Wrapper to run the Hybrid universal test
# Usage:
#   ./scripts/aurora_device_test.sh           -> run hybrid (auto-detect embedded)
#   ./scripts/aurora_device_test.sh --force esp32
#   ./scripts/aurora_device_test.sh --auto-approve
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${PYTHON:-python3}"
CMD="$PY tools/device_test_runner.py"
ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --auto-approve) ARGS+=("--auto-approve"); shift ;;
    --force) shift; ARGS+=("--force-target"); ARGS+=("$1"); shift ;;
    --clean) ARGS+=("--clean"); shift ;;
    *) echo "Unknown arg $1"; exit 1 ;;
  esac
done

echo "Running Aurora device hybrid test: ${ARGS[*]:-default}"
$CMD "${ARGS[@]}"
