# 🐧 Aurora-X for Linux - Complete Guide

## What's Been Fixed for Linux

✅ **Cross-platform x-start script** - Detects Linux automatically  
✅ **Installation script** - `install-linux.sh` for automated setup  
✅ **Test script** - `test-linux.sh` validates your environment  
✅ **Helper scripts** - `start-aurora.sh` and `stop-aurora.sh`  
✅ **Requirements.txt** - All Python dependencies listed  
✅ **Systemd support** - Run Aurora as a system service  
✅ **Virtual environment** - Isolated Python environment  
✅ **Port configuration** - Chat server properly configured for port 5003

---

## 🚀 Quick Start (Copy & Paste)

```bash
# 1. Navigate to Aurora directory
cd Aurora-x

# 2. Run installation script
chmod +x install-linux.sh
./install-linux.sh

# 3. Start Aurora
./start-aurora.sh

# 4. Access Aurora
# Frontend: http://localhost:5000
# Chat: http://localhost:5003
# Dashboard: http://localhost:5005
```

That's it! 🎉

---

## 📋 Prerequisites

### Required:
- **Python 3.8+** (`python3 --version`)
- **pip** (`pip3 --version`)
- **Node.js 18+** (`node --version`)
- **npm 9+** (`npm --version`)

### Install on Ubuntu/Debian:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs npm git curl
```

### Install on Fedora/RHEL:
```bash
sudo dnf install python3 python3-pip nodejs npm git curl
```

### Install on Arch:
```bash
sudo pacman -S python python-pip nodejs npm git curl
```

---

## 📦 What Gets Installed

### Python Packages:
- `flask` - Web framework for chat server
- `flask-cors` - Cross-origin resource sharing
- `fastapi` - Modern API framework
- `uvicorn` - ASGI server
- `requests` - HTTP library
- `aiohttp` - Async HTTP
- Plus all dependencies in `requirements.txt`

### Node Packages:
- React and UI libraries
- Vite build tool
- Development dependencies

### System Services:
- Backend API (port 5000)
- Bridge Service (port 5001)
- Self-Learning (port 5002)
- Chat Server (port 5003)
- Luminar Dashboard (port 5005)
- Autonomous Monitor (background)

---

## 🛠️ Installation Options

### Option 1: Automated (Recommended)

```bash
chmod +x install-linux.sh
./install-linux.sh
```

This script:
- ✅ Checks all dependencies
- ✅ Creates virtual environment
- ✅ Installs Python packages
- ✅ Installs Node packages
- ✅ Makes scripts executable
- ✅ Tests Aurora Core
- ✅ Checks port availability
- ✅ Creates helper scripts
- ✅ (Optional) Sets up systemd service

### Option 2: Manual

```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Install Node dependencies
npm install

# 4. Make scripts executable
chmod +x x-start x-stop
chmod +x *.sh

# 5. Test installation
./test-linux.sh

# 6. Start Aurora
python3 x-start
```

### Option 3: Docker (Coming Soon)

```bash
docker-compose up -d
```

---

## 🎯 Usage

### Starting Aurora

```bash
# Method 1: Helper script (easiest)
./start-aurora.sh

# Method 2: Direct command
python3 x-start

# Method 3: With virtual environment
source .venv/bin/activate
python3 x-start

# Method 4: As systemd service
sudo systemctl start aurora
```

### Stopping Aurora

```bash
# Method 1: Helper script
./stop-aurora.sh

# Method 2: Direct command
python3 x-stop

# Method 3: Systemd
sudo systemctl stop aurora
```

### Checking Status

```bash
# Check if services are running
netstat -tlnp | grep -E '5000|5001|5002|5003|5005'

# Or with lsof
sudo lsof -i -P -n | grep -E '5000|5001|5002|5003|5005'

# Systemd status
sudo systemctl status aurora
```

---

## 🧪 Testing

### Run All Tests
```bash
./test-linux.sh
```

### Manual Tests

**Test Aurora Core:**
```bash
python3 -c "from aurora_core import create_aurora_core; aurora = create_aurora_core(); print('✅ Aurora Core OK')"
```

**Test Chat Server:**
```bash
# Start chat server
python3 aurora_chat_server.py --port 5003 &

# Test endpoint
curl -X POST http://localhost:5003/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello Aurora","session_id":"test"}'

# Should return JSON with Aurora's response
```

**Test Health Endpoint:**
```bash
curl http://localhost:5003/api/health
# Should return: {"status":"healthy","server":"Aurora Core Chat"}
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:
```bash
AURORA_ENV=production
AURORA_HOST=0.0.0.0
AURORA_PORT=5000
CHAT_PORT=5003
BRIDGE_PORT=5001
SELF_LEARN_PORT=5002
DASHBOARD_PORT=5005
```

### Port Configuration

Edit `x-start` to change ports:
```python
# Line 43: Frontend/Backend port
start_process(["npm", "run", "dev"])  # Uses 5000

# Line 53: Chat server port
start_process([PYTHON_CMD, "aurora_chat_server.py", "--port", "5003"])
```

Or run chat server manually:
```bash
python3 aurora_chat_server.py --port 9000  # Custom port
```

---

## 🐛 Troubleshooting

### Chat Server Won't Start

**Error: "Address already in use"**
```bash
# Find and kill process on port 5003
sudo lsof -ti :5003 | xargs sudo kill -9

# Or use a different port
python3 aurora_chat_server.py --port 9000
```

**Error: "ModuleNotFoundError: No module named 'flask'"**
```bash
# Activate virtual environment
source .venv/bin/activate

# Install Flask
pip install flask flask-cors
```

**Error: "Cannot import name 'create_aurora_core'"**
```bash
# Check if aurora_core.py exists
ls -la aurora_core.py

# Check Python path
python3 -c "import sys; print(sys.path)"

# Make sure you're in Aurora-x directory
pwd
```

### Services Won't Start

**Check Python version:**
```bash
python3 --version
# Should be 3.8 or higher
```

**Check Node version:**
```bash
node --version
# Should be 18 or higher
```

**Check virtual environment:**
```bash
which python3
# Should show .venv/bin/python3 when activated
```

**Check all dependencies:**
```bash
./test-linux.sh
```

### Permission Denied

```bash
# Make all scripts executable
chmod +x install-linux.sh test-linux.sh tell-aurora-linux.sh
chmod +x start-aurora.sh stop-aurora.sh
chmod +x x-start x-stop
```

### Firewall Issues

**Ubuntu (ufw):**
```bash
sudo ufw allow 5000:5005/tcp
sudo ufw reload
```

**Fedora/RHEL (firewalld):**
```bash
sudo firewall-cmd --add-port=5000-5005/tcp --permanent
sudo firewall-cmd --reload
```

### Virtual Environment Not Working

```bash
# Recreate virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🚀 Production Deployment

### Use Gunicorn (Production WSGI Server)

```bash
# Install Gunicorn
pip install gunicorn

# Run chat server with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5003 --timeout 120 aurora_chat_server:app
```

### Use Nginx as Reverse Proxy

```nginx
# /etc/nginx/sites-available/aurora

server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Chat API
    location /api/chat {
        proxy_pass http://localhost:5003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 120s;
    }

    # Dashboard
    location /dashboard {
        proxy_pass http://localhost:5005;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/aurora /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Systemd Service

Create `/etc/systemd/system/aurora.service`:

```ini
[Unit]
Description=Aurora-X AI System
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/Aurora-x
Environment="PATH=/home/your-username/Aurora-x/.venv/bin:/usr/local/bin:/usr/bin"
ExecStart=/home/your-username/Aurora-x/.venv/bin/python3 /home/your-username/Aurora-x/x-start
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable aurora
sudo systemctl start aurora
sudo systemctl status aurora
```

View logs:
```bash
sudo journalctl -u aurora -f
```

---

## 📊 Monitoring

### Check Service Status
```bash
# All ports
netstat -tlnp | grep -E '5000|5001|5002|5003|5005'

# Specific service
curl http://localhost:5003/api/health
curl http://localhost:5000/api/health
```

### View Logs
```bash
# If running with systemd
sudo journalctl -u aurora -f

# If running manually
tail -f aurora_*.log
```

### Resource Usage
```bash
# CPU and Memory
ps aux | grep -E 'python3|node'

# Detailed with htop
htop
```

---

## 🔄 Updating Aurora

```bash
# Stop services
./stop-aurora.sh

# Update code
git pull origin main

# Update dependencies
source .venv/bin/activate
pip install -r requirements.txt --upgrade
npm install

# Restart services
./start-aurora.sh
```

---

## 📚 Additional Resources

- **Terminal Commands**: `cat AURORA_TERMINAL_COMMANDS.md`
- **Linux Chat Fix**: `cat LINUX_CHAT_FIX.md`
- **Installation Details**: `cat INSTALL_LINUX.md`
- **Architecture**: `cat AURORA_COMPLETE_ARCHITECTURE_*.md`

---

## ✅ Success Checklist

Before reporting issues, verify:

- [ ] Python 3.8+ installed (`python3 --version`)
- [ ] pip installed (`pip3 --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] npm installed (`npm --version`)
- [ ] Virtual environment created (`.venv/` directory exists)
- [ ] Virtual environment activated (`which python3` shows `.venv/bin/python3`)
- [ ] Python packages installed (`pip list | grep flask`)
- [ ] Node packages installed (`ls node_modules/`)
- [ ] Scripts are executable (`ls -la x-start x-stop`)
- [ ] Ports available (`sudo lsof -i :5003`)
- [ ] Aurora Core imports (`python3 -c "from aurora_core import create_aurora_core"`)
- [ ] Test script passes (`./test-linux.sh`)
- [ ] Services start (`python3 x-start`)
- [ ] Chat responds (`curl http://localhost:5003/api/health`)

---

## 🎉 You're Ready!

Aurora is now fully compatible with Linux. The chat server will:
- ✅ Start on port 5003
- ✅ Use Flask with CORS enabled
- ✅ Load Aurora Core Intelligence
- ✅ Process conversations asynchronously
- ✅ Respond to system management commands
- ✅ Serve the Cosmic Nexus interface

**Start Aurora:**
```bash
./start-aurora.sh
```

**Access:**
- Frontend: http://localhost:5000
- Chat: http://localhost:5003
- Dashboard: http://localhost:5005

**Enjoy! 🌟**
