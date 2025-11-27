aaaq# 🐧 Aurora Linux Chat Installation Fix

## Issue: Chat Failed on Linux

### Common Problems & Solutions

#### 1. **Missing Python Dependencies**
```bash
# Install required packages
pip install flask flask-cors requests

# Or install all requirements
pip install -r requirements.txt
```

#### 2. **Wrong Port Configuration**
The chat server runs on port **9000** by default, but Aurora expects it on **5003**.

**Fix Option A - Run on correct port:**
```bash
python3 aurora_chat_server.py --port 5003
```

**Fix Option B - Update x-start to use port 9000:**
Edit `x-start` and change chat server port from 5003 to 9000.

#### 3. **Aurora Core Not Found**
```bash
# Make sure aurora_core.py exists and is importable
python3 -c "from aurora_core import create_aurora_core; print('✅ Aurora Core OK')"
```

#### 4. **Permission Issues on Linux**
```bash
# Make scripts executable
chmod +x x-start
chmod +x x-stop
chmod +x aurora_chat_server.py
```

#### 5. **Firewall Blocking Ports**
```bash
# Check if ports are accessible
sudo netstat -tlnp | grep -E '5000|5003|9000'

# Allow ports through firewall (if using ufw)
sudo ufw allow 5000/tcp
sudo ufw allow 5003/tcp
sudo ufw allow 9000/tcp
```

---

## Step-by-Step Linux Installation

### 1. Install System Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs npm

# Fedora/RHEL
sudo dnf install python3 python3-pip nodejs npm

# Arch
sudo pacman -S python python-pip nodejs npm
```

### 2. Create Virtual Environment
```bash
cd Aurora-x
python3 -m venv .venv
source .venv/bin/activate  # On Linux
```

### 3. Install Python Dependencies
```bash
pip install --upgrade pip
pip install flask flask-cors requests aiohttp fastapi uvicorn
pip install -r requirements.txt
```

### 4. Install Node Dependencies
```bash
cd client
npm install
cd ..
```

### 5. Configure Chat Server
```bash
# Option A: Run chat on port 5003 (recommended)
python3 aurora_chat_server.py --port 5003

# Option B: Update x-start script
# Change port 5003 to 9000 in the x-start file
```

### 6. Start Aurora
```bash
# Make executable
chmod +x x-start x-stop

# Start services
python3 x-start
```

---

## Quick Diagnostic Commands

### Test Chat Server
```bash
# Check if chat server is running
curl -X POST http://localhost:5003/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello Aurora","session_id":"test"}'

# Or on port 9000
curl -X POST http://localhost:9000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello Aurora","session_id":"test"}'
```

### Check All Ports
```bash
# See what's running
netstat -tlnp | grep -E '5000|5001|5002|5003|5173|9000'
```

### Test Aurora Core
```bash
python3 -c "
from aurora_core import create_aurora_core
aurora = create_aurora_core()
print('✅ Aurora Core loaded successfully')
print(f'Tiers: {aurora.tier_count}')
"
```

---

## Common Error Messages & Fixes

### Error: "ModuleNotFoundError: No module named 'flask'"
**Fix:**
```bash
pip install flask flask-cors
```

### Error: "Address already in use"
**Fix:**
```bash
# Kill process on port
sudo fuser -k 5003/tcp
# Or
sudo kill $(sudo lsof -t -i:5003)
```

### Error: "Cannot import name 'create_aurora_core'"
**Fix:**
```bash
# Check if aurora_core.py exists
ls -la aurora_core.py

# If missing or corrupted, the file should be in your repo
python3 -c "import aurora_core; print(aurora_core.__file__)"
```

### Error: "Permission denied" when running x-start
**Fix:**
```bash
chmod +x x-start x-stop
python3 x-start  # Or use python3 explicitly
```

---

## Automated Fix Script

Run this to auto-diagnose and fix common issues:

```bash
python3 aurora_diagnose_chat.py
```

---

## Tell Aurora About the Failure

Once you identify the specific error, you can tell Aurora:

```bash
# Start a Python shell
python3

# Then:
from aurora_core import AuroraKnowledgeTiers
aurora = AuroraKnowledgeTiers()

# Tell Aurora what failed
aurora.log_system_event({
    "event": "chat_failure_linux",
    "platform": "linux",
    "error": "YOUR_ERROR_MESSAGE_HERE",
    "port_attempted": 5003,
    "timestamp": "2025-11-18"
})
```

Or use the direct conversation script:
```bash
python3 ask_aurora_directly.py
# Then type: "Chat failed on Linux installation with error: [YOUR ERROR]"
```

---

## Linux-Specific x-start Configuration

The `x-start` script should be cross-platform. If it's not working:

```bash
# Verify platform detection
python3 -c "import platform; print(platform.system())"
# Should output: Linux

# Check if x-start is detecting Linux correctly
grep -A 5 "IS_WINDOWS" x-start
```

---

## Port Configuration Summary

| Service | Default Port | Purpose |
|---------|-------------|---------|
| Backend | 5000 | Main API |
| Bridge | 5001 | Service bridge |
| Self-Learn | 5002 | Learning system |
| Chat | 5003 or 9000 | Chat interface |
| Luminar | 5005 | Dashboard |
| Frontend | 5173 | Vite dev server |

**The mismatch:** `aurora_chat_server.py` defaults to **9000**, but Aurora expects **5003**.

**Solution:** Always run with `--port 5003` flag.

---

## Working Linux Command

```bash
# Full startup sequence
source .venv/bin/activate  # Activate virtual environment
python3 x-start            # Start all services

# Or manually start chat on correct port
python3 aurora_chat_server.py --port 5003 &
```

---

## Need More Help?

Run the diagnostic:
```bash
python3 aurora_diagnose_chat.py
```

This will test all endpoints and show you exactly what's failing.
