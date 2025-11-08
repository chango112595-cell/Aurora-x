#!/bin/bash
# Aurora Diagnostic System Startup
# 1. Generate diagnostic snapshot
# 2. Start diagnostic server (no side effects, read-only)
# 3. Display URL to access

echo ""
echo "========================================"
echo "🔍 Aurora Diagnostic System Startup"
echo "========================================"
echo ""

cd /workspaces/Aurora-x

# Step 1: Generate diagnostic snapshot
echo "📊 Generating diagnostic snapshot..."
python /workspaces/Aurora-x/tools/generate_diagnostics.py

echo ""
echo "✅ Diagnostic data generated"
echo ""

# Step 2: Show what was found
if [ -f /tmp/diag_output.txt ]; then
    cat /tmp/diag_output.txt
fi

echo ""
echo "========================================"
echo "🚀 Starting Diagnostic Server"
echo "========================================"
echo ""
echo "📡 Diagnostic Web Server starting on port 9999..."
echo ""
echo "🌐 View Dashboard at:"
echo "   http://127.0.0.1:9999"
echo ""
echo "📡 API Endpoints:"
echo "   http://127.0.0.1:9999/api/status"
echo "   http://127.0.0.1:9999/api/port/5000"
echo ""
echo "========================================"
echo ""

# Step 3: Start diagnostic server (runs indefinitely)
python /workspaces/Aurora-x/diagnostic_server.py
