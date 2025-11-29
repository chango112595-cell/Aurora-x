
#!/bin/bash
# Check which Luminar Nexus version is active

echo "Checking Luminar Nexus status..."
echo ""

# Check v2 status endpoint
echo "=== Luminar Nexus v2 Status ==="
curl -s http://localhost:5000/api/luminar-nexus/status | python3 -m json.tool

echo ""
echo "=== Chat Integration Status ==="
curl -s -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "are you using luminar nexus v2?", "session_id": "test"}' \
  | python3 -m json.tool
