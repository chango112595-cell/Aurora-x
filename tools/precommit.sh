#!/usr/bin/env bash
#
# Pre-commit hook script for progress tracking and docs sync.
# Ensures progress tracking and documentation stay in sync.
#
set -e  # Exit on error

echo "🔄 Running progress update..."

# Run update_progress.py
if ! python3 tools/update_progress.py; then
    echo "❌ Progress update failed"
    exit 1
fi

echo ""
echo "📝 Updating summary documentation..."

# Run update_summary_md.py
if ! python3 tools/update_summary_md.py; then
    echo "❌ Summary update failed"
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
echo "📊 Checking for documentation drift..."

# Run check_task_drift.py
if ! python3 tools/check_task_drift.py; then
    echo "⚠️  Documentation drift detected (non-fatal)"
    # Don't exit on drift - just warn
fi

echo ""
echo "✅ Pre-commit checks passed successfully!"
echo ""
echo "Don't forget to add and commit:"
echo "  - progress.json"
echo "  - MASTER_TASK_LIST.md"
echo "  - aurora_X.md (if updated)"

exit 0