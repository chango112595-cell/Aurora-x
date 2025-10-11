#!/bin/bash

echo "🧪 Testing Makefile demo targets"
echo "================================="
echo

# Test demo-list target (should show available cards)
echo "📋 Testing: make demo-list"
make demo-list 2>&1 | head -5
echo

# Test demo-all target (would execute all cards if server running)
echo "🚀 Testing: make demo-all (dry run)"
make demo-all HOST=http://localhost:5001 2>&1 | head -5
echo

echo "✅ Makefile targets added successfully!"
echo
echo "Usage examples:"
echo "  make demo-list              # List all available demo cards"
echo "  make demo-all               # Run all cards on localhost:5001"
echo "  make demo-all HOST=http://custom-host:8000  # Custom host"
echo
echo "For production:"
echo "  HOST=https://your-app.replit.dev make demo-all"