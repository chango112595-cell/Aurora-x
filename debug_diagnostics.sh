#!/bin/bash
# Debug diagnostic system - show errors clearly

cd /workspaces/Aurora-x

echo ""
echo "========================================"
echo "🔍 AURORA DIAGNOSTIC DEBUG"
echo "========================================"
echo ""

# Check if generate_diagnostics.py exists
echo "1️⃣  Checking for generate_diagnostics.py..."
if [ -f tools/generate_diagnostics.py ]; then
    echo "   ✅ File exists"
else
    echo "   ❌ File NOT found!"
    exit 1
fi

# Try running it with full error output
echo ""
echo "2️⃣  Running diagnostic generator..."
echo "   (All output below)"
echo "---"
python tools/generate_diagnostics.py

echo "---"
echo ""

# Check if diagnostics.json was created
echo "3️⃣  Checking for diagnostics.json..."
if [ -f tools/diagnostics.json ]; then
    echo "   ✅ File created!"
    echo ""
    echo "   File contents:"
    cat tools/diagnostics.json
else
    echo "   ❌ File was NOT created"
fi

echo ""
echo "========================================"
echo ""
