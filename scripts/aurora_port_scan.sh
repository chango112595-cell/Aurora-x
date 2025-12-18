
#!/bin/bash
echo -e "\n=== AURORA SERVER DIAGNOSTIC REPORT ===\n"

echo "▶ Checking Listening Ports..."
if command -v lsof &> /dev/null; then
    sudo lsof -i -P -n | grep LISTEN || echo "No listening ports detected"
elif command -v netstat &> /dev/null; then
    netstat -tuln | grep LISTEN || echo "No listening ports detected"
else
    echo "⚠ Neither lsof nor netstat found. Install one to check ports."
fi

echo -e "\n▶ Checking Express Backend (5000)..."
if command -v lsof &> /dev/null; then
    if sudo lsof -i:5000 -sTCP:LISTEN >/dev/null 2>&1; then
        echo "✔ Express backend running on port 5000"
        sudo lsof -i:5000 -sTCP:LISTEN
    else
        echo "✘ Express backend NOT running on port 5000"
    fi
elif command -v netstat &> /dev/null; then
    if netstat -tuln | grep ":5000" >/dev/null 2>&1; then
        echo "✔ Port 5000 is in use"
        netstat -tuln | grep ":5000"
    else
        echo "✘ Port 5000 is not in use"
    fi
fi

for P in 8000 8100 9000; do
    echo -e "\n▶ Checking Python AI backend on port $P..."
    if command -v lsof &> /dev/null; then
        if sudo lsof -i:$P -sTCP:LISTEN >/dev/null 2>&1; then
            echo "✔ AI backend detected on port $P"
            sudo lsof -i:$P -sTCP:LISTEN
        else
            echo "✘ No AI backend on port $P"
        fi
    elif command -v netstat &> /dev/null; then
        if netstat -tuln | grep ":$P" >/dev/null 2>&1; then
            echo "✔ Port $P is in use"
            netstat -tuln | grep ":$P"
        else
            echo "✘ Port $P is not in use"
        fi
    fi
done

echo -e "\n▶ Checking Node.js Processes..."
ps aux | grep -i node | grep -v grep || echo "No Node.js processes found"

echo -e "\n▶ Checking Python Processes..."
ps aux | grep -i python | grep -v grep || echo "No Python processes found"

echo -e "\n▶ Checking Replit Processes..."
ps aux | grep -E "(npm|tsx|python3)" | grep -v grep || echo "No dev server processes found"

echo -e "\n=== END OF DIAGNOSTIC REPORT ===\n"
