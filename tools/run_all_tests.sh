#!/bin/bash
# Run all Aurora-X tests with comprehensive reporting

set -e

echo "🧪 Running Aurora-X test suite..."
echo "================================"

# Check Python environment
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

# Check pytest
if ! python3 -c "import pytest" 2>/dev/null; then
    echo "⚠️  pytest not installed, installing..."
    pip install pytest pytest-cov
fi

# Run tests with coverage
echo ""
echo "Running tests with coverage..."
python3 -m pytest tests/ -v --cov=aurora_x --cov-report=term-missing --cov-report=html

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed"
else
    echo ""
    echo "❌ Some tests failed"
    exit 1
fi
