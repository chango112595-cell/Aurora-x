
#!/bin/bash
# Start Luminar Nexus V2 with all advanced features

echo "🌌 Starting Luminar Nexus V2..."
echo "   Version: 2.0.0"
echo "   Port: 5005"
echo ""

# Start V2 API server
python3 tools/luminar_nexus_v2.py serve &

# Wait for startup
sleep 3

# Check if running
if curl -s http://127.0.0.1:5005/api/nexus/status > /dev/null; then
    echo "✅ Luminar Nexus V2 is running!"
    echo "   API: http://127.0.0.1:5005"
    echo "   Status: http://127.0.0.1:5005/api/nexus/status"
    echo "   Features: AI healing, Quantum mesh, Port management"
else
    echo "❌ V2 failed to start - check logs"
fi
