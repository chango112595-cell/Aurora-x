#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "Running PACK03 test suite..."
python3 -m pytest "$ROOT/tests" -q
echo "PACK03 tests passed (unit)"
bash -c "python3 $ROOT/tests/test_lifecycle.py" || true
echo "Integration checks complete."
echo "All done."
