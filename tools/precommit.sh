#!/usr/bin/env bash
#
# Pre-commit hook script for progress tracking.
# Runs update_progress.py followed by check_progress_regression.py

set -e  # Exit on error

echo "🔄 Running progress update..."

# Run update_progress.py
if ! python3 tools/update_progress.py; then
    echo "❌ Progress update failed"
    exit 1
fi

echo ""
echo "🔍 Checking for regressions..."

# Run check_progress_regression.py
if ! python3 tools/check_progress_regression.py; then
    echo "❌ Regression check failed"
    exit 1
fi

echo ""
echo "✅ Pre-commit checks passed successfully!"
echo ""
echo "Don't forget to add and commit both:"
echo "  - progress.json"
echo "  - MASTER_TASK_LIST.md"

exit 0