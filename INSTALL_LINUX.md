# 🐧 Aurora Linux Quick Start

## One-Command Installation

```bash
# Clone or download Aurora-X, then:
chmod +x install-linux.sh
./install-linux.sh
```

---

## Manual Installation

### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs npm
```

**Fedora/RHEL/CentOS:**
```bash
sudo dnf install python3 python3-pip nodejs npm
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip nodejs npm
```

### 2. Install Aurora

```bash
cd Aurora-x

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies
npm install
```

### 3. Make Scripts Executable

```bash
chmod +x x-start x-stop install-linux.sh test-linux.sh
```

### 4. Test Installation

```bash
./test-linux.sh
```

### 5. Start Aurora

```bash
# Option 1: Using helper script
./start-aurora.sh

# Option 2: Direct command
python3 x-start

# Option 3: With virtual environment
source .venv/bin/activate
python3 x-start
```

---

## Access Aurora

- 🌐 **Frontend**: http://localhost:5000
- 💬 **Chat**: http://localhost:5003  
- 📊 **Dashboard**: http://localhost:5005

---

## Stop Aurora

```bash
./stop-aurora.sh
# OR
python3 x-stop
```

---

## Troubleshooting

### Chat Server Won't Start

**Problem**: Port 5003 already in use
```bash
# Find what's using the port
sudo lsof -i :5003

# Kill the process
sudo kill $(sudo lsof -t -i:5003)

# Or use different port
python3 aurora_chat_server.py --port 9000
```

**Problem**: Flask not installed
```bash
pip install flask flask-cors
```

**Problem**: Aurora Core not found
```bash
# Check if file exists
ls -la aurora_core.py

# Test import
python3 -c "from aurora_core import create_aurora_core; print('OK')"
```

### Services Won't Start

**Check all dependencies:**
```bash
./test-linux.sh
```

**Check Python packages:**
```bash
pip list | grep -E 'flask|cors|requests|fastapi'
```

**Check Node packages:**
```bash
npm list --depth=0
```

### Permission Issues

```bash
# Make all Python scripts executable
find . -name "*.py" -type f -exec chmod +x {} \;

# Make shell scripts executable  
chmod +x *.sh x-start x-stop
```

### Port Conflicts

```bash
# Check all Aurora ports
netstat -tlnp | grep -E '5000|5001|5002|5003|5005'

# Or with lsof
sudo lsof -i -P -n | grep -E '5000|5001|5002|5003|5005'
```

---

## Run as Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/aurora.service
```

Paste this:
```ini
[Unit]
Description=Aurora-X AI System
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/Aurora-x
Environment="PATH=/path/to/Aurora-x/.venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/path/to/Aurora-x/.venv/bin/python3 /path/to/Aurora-x/x-start
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable aurora.service
sudo systemctl start aurora.service
sudo systemctl status aurora.service
```

---

## Environment Setup

Create `.env` file if needed:
```bash
cat > .env <<EOF
AURORA_ENV=production
AURORA_HOST=0.0.0.0
AURORA_PORT=5000
CHAT_PORT=5003
EOF
```

---

## Common Linux-Specific Issues

### 1. **Virtual Environment Not Activating**
```bash
# Use full path
source /full/path/to/Aurora-x/.venv/bin/activate

# Or
. .venv/bin/activate
```

### 2. **Python Version Issues**
```bash
# Check version
python3 --version

# Should be 3.8 or higher
# If not, install newer Python:
sudo apt install python3.11
python3.11 -m venv .venv
```

### 3. **npm EACCES Errors**
```bash
# Fix npm permissions
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### 4. **Firewall Blocking Ports**
```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 5000/tcp
sudo ufw allow 5003/tcp
sudo ufw allow 5005/tcp

# Fedora/RHEL (firewalld)
sudo firewall-cmd --add-port=5000/tcp --permanent
sudo firewall-cmd --add-port=5003/tcp --permanent
sudo firewall-cmd --add-port=5005/tcp --permanent
sudo firewall-cmd --reload
```

---

## Verify Installation

```bash
# All tests should pass
./test-linux.sh

# Test chat endpoint
curl -X POST http://localhost:5003/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello Aurora","session_id":"test"}'

# Should return JSON response
```

---

## Update Aurora

```bash
git pull origin main
pip install -r requirements.txt --upgrade
npm install
./start-aurora.sh
```

---

## Uninstall

```bash
# Stop services
python3 x-stop

# Remove systemd service
sudo systemctl stop aurora
sudo systemctl disable aurora
sudo rm /etc/systemd/system/aurora.service

# Remove virtual environment
rm -rf .venv

# Remove node modules
rm -rf node_modules

# Keep source code or delete entire directory
# rm -rf Aurora-x
```

---

## Performance Tips

### Use Production Server (not Flask dev server)

Install Gunicorn:
```bash
pip install gunicorn
```

Run chat with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5003 aurora_chat_server:app
```

### Run in Background with tmux

```bash
# Install tmux
sudo apt install tmux

# Start tmux session
tmux new -s aurora

# Start Aurora
python3 x-start

# Detach: Ctrl+B, then D
# Reattach: tmux attach -t aurora
```

---

## Success Checklist

- ✅ Python 3.8+ installed
- ✅ Node.js 18+ and npm installed  
- ✅ Virtual environment created (`.venv/`)
- ✅ Python packages installed (`pip list`)
- ✅ Node packages installed (`node_modules/`)
- ✅ Scripts executable (`chmod +x`)
- ✅ Ports available (5000, 5001, 5002, 5003, 5005)
- ✅ Aurora Core imports (`python3 -c "from aurora_core import create_aurora_core"`)
- ✅ Services start (`python3 x-start`)
- ✅ Chat responds (`curl http://localhost:5003/api/health`)

---

**Need Help?** Run: `./test-linux.sh` to diagnose issues!
