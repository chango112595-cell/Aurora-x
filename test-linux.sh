#!/bin/bash
# Quick Aurora Linux Test
# Tests if Aurora can run on Linux

echo "🧪 Aurora Linux Compatibility Test"
echo "==================================="
echo ""

# Test 1: Python
echo "1️⃣ Testing Python..."
if python3 --version; then
    echo "✅ Python OK"
else
    echo "❌ Python 3 not found"
    exit 1
fi

# Test 2: Aurora Core Import
echo ""
echo "2️⃣ Testing Aurora Core..."
if python3 -c "from aurora_core import create_aurora_core; print('✅ Aurora Core imports OK')"; then
    echo "✅ Aurora Core OK"
else
    echo "❌ Aurora Core failed to import"
    exit 1
fi

# Test 3: Flask
echo ""
echo "3️⃣ Testing Flask..."
if python3 -c "import flask; import flask_cors; print('✅ Flask OK')"; then
    echo "✅ Flask and CORS OK"
else
    echo "❌ Flask not installed"
    echo "Install: pip3 install flask flask-cors"
    exit 1
fi

# Test 4: Chat Server Syntax
echo ""
echo "4️⃣ Testing Chat Server..."
if python3 -m py_compile aurora_chat_server.py; then
    echo "✅ Chat server syntax OK"
else
    echo "❌ Chat server has syntax errors"
    exit 1
fi

# Test 5: Ports Available
echo ""
echo "5️⃣ Checking ports..."
for port in 5000 5001 5002 5003 5005; do
    if command -v lsof &> /dev/null; then
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "⚠️  Port $port already in use"
        else
            echo "✅ Port $port available"
        fi
    else
        echo "⚠️  lsof not available, skipping port check"
        break
    fi
done

# Test 6: Node.js
echo ""
echo "6️⃣ Testing Node.js..."
if command -v node &> /dev/null; then
    echo "✅ Node.js $(node --version) OK"
else
    echo "⚠️  Node.js not found (needed for frontend)"
fi

# Test 7: npm
echo ""
echo "7️⃣ Testing npm..."
if command -v npm &> /dev/null; then
    echo "✅ npm $(npm --version) OK"
else
    echo "⚠️  npm not found (needed for frontend)"
fi

# Summary
echo ""
echo "=================================="
echo "✅ Aurora is compatible with Linux!"
echo "=================================="
echo ""
echo "To install:"
echo "  chmod +x install-linux.sh"
echo "  ./install-linux.sh"
echo ""
echo "Or manually:"
echo "  pip3 install -r requirements.txt"
echo "  npm install"
echo "  python3 x-start"
