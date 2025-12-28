
#!/bin/bash
# Start Luminar Nexus V2 with all advanced features

LUMINAR_HOST="${LUMINAR_HOST:-${AURORA_HOST:-localhost}}"
LUMINAR_PORT="${LUMINAR_PORT:-8000}"
LUMINAR_MODE="${LUMINAR_MODE:-auto}"

echo "🌌 Starting Luminar Nexus V2..."
echo "   Version: 2.0.0"
echo "   Host: ${LUMINAR_HOST}"
echo "   Port: ${LUMINAR_PORT}"
echo ""

AURORA_HOST="${AURORA_HOST:-127.0.0.1}"
BASE_URL="http://${AURORA_HOST}:5005"

# Start V2 API server
python3 tools/luminar_nexus_v2.py serve &

# Wait for startup
sleep 3

# Check if running
if curl -s "${BASE_URL}/api/nexus/status" > /dev/null; then
    echo "✅ Luminar Nexus V2 is running!"
    echo "   API: ${BASE_URL}"
    echo "   Status: ${BASE_URL}/api/nexus/status"
    echo "   Features: AI healing, Quantum mesh, Port management"
else
    echo "❌ V2 failed to start - check logs"
fi
