
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

if [ "${LUMINAR_MODE}" = "auto" ]; then
    if [ "${LUMINAR_PORT}" = "5005" ]; then
        LUMINAR_MODE="api"
    else
        LUMINAR_MODE="serve"
    fi
fi

if [ "${LUMINAR_MODE}" = "serve" ] && [ "${LUMINAR_PORT}" != "8000" ]; then
    echo "⚠️  Note: luminar_nexus_v2.py serve binds to port 8000 regardless of LUMINAR_PORT."
    echo "   Switching health checks to port 8000. Set LUMINAR_MODE=api for port 5005."
    echo ""
    LUMINAR_PORT="8000"
fi

if [ "${LUMINAR_MODE}" = "serve" ]; then
    # Start V2 API server (serve binds to 8000)
    python3 tools/luminar_nexus_v2.py serve &
elif [ "${LUMINAR_MODE}" = "api" ]; then
    # Start V2 API server (api binds to 5005)
    python3 tools/luminar_nexus_v2.py api &
else
    echo "❌ Unknown LUMINAR_MODE=${LUMINAR_MODE}. Use 'auto', 'serve', or 'api'."
    exit 1
fi

# Wait for startup
sleep 3

# Check if running
if curl -s "http://${LUMINAR_HOST}:${LUMINAR_PORT}/api/nexus/status" > /dev/null; then
    echo "✅ Luminar Nexus V2 is running!"
    echo "   API: http://${LUMINAR_HOST}:${LUMINAR_PORT}"
    echo "   Status: http://${LUMINAR_HOST}:${LUMINAR_PORT}/api/nexus/status"
    echo "   Features: AI healing, Quantum mesh, Port management"
else
    echo "❌ V2 failed to start - check logs"
fi
