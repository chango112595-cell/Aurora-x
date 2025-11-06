#!/bin/bash
# Simple telemetry function to talk to Aurora
if [ -z "$1" ]; then
  echo "Usage: ./ask-aurora.sh \"Your question\""
  exit 1
fi
curl -s -X POST http://localhost:5003/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"$1\"}" | python3 -c "import sys, json; print(json.load(sys.stdin).get('response', 'No response'))"
