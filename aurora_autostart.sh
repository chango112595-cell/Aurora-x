#!/bin/bash
#
# Aurora Auto-Start Script
# Runs on container boot to restore all services
# Install: Add to .bashrc or create systemd user service
#

ORCHESTRATOR="/workspaces/Aurora-x/aurora_orchestrator.sh"
LOCK_FILE="/tmp/aurora_autostart.lock"

# Prevent multiple simultaneous runs
if [ -f "$LOCK_FILE" ]; then
    echo "⚠️  Auto-start already running (lock file exists)"
    exit 0
fi

touch "$LOCK_FILE"

# Wait a bit for system to stabilize
sleep 5

echo "🚀 Aurora Auto-Start: Launching services..."

# Start orchestrator
if [ -x "$ORCHESTRATOR" ]; then
    "$ORCHESTRATOR" start
    echo "✅ Services started successfully"
else
    echo "❌ Orchestrator not found or not executable"
fi

rm "$LOCK_FILE"
