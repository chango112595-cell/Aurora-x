
#!/bin/bash
# Start Luminar Nexus V2 with all advanced features

echo "🌌 Starting Luminar Nexus V2..."
echo "   Version: 2.0.0"
LUMINAR_HOST="${AURORA_HOST:-localhost}"
LUMINAR_PORT="${AURORA_NEXUS_V2_PORT:-5005}"
LUMINAR_BASE_URL="http://${LUMINAR_HOST}:${LUMINAR_PORT}"
echo "   Host: ${LUMINAR_HOST}"
echo "   Port: ${LUMINAR_PORT}"
echo ""

# Start V2 API server
python3 tools/luminar_nexus_v2.py serve &

# Wait for startup
sleep 3

# Check if running
if curl -s "${LUMINAR_BASE_URL}/api/nexus/status" > /dev/null; then
    echo "✅ Luminar Nexus V2 is running!"
    echo "   API: ${LUMINAR_BASE_URL}"
    echo "   Status: ${LUMINAR_BASE_URL}/api/nexus/status"
    echo "   Features: AI healing, Quantum mesh, Port management"
else
    echo "❌ V2 failed to start - check logs"
fi
