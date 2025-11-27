#!/bin/bash
# Aurora-X Linux Installation Script
# Run this on your Linux system to install Aurora

set -e  # Exit on error

echo "🌌 Aurora-X Linux Installation"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo -e "${RED}❌ This script is for Linux only${NC}"
    exit 1
fi

# Check Python version
echo "🔍 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Install Python 3: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"

# Check Node.js
echo "🔍 Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node.js not found${NC}"
    echo "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✅ Node.js $NODE_VERSION found${NC}"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed${NC}"
    exit 1
fi

# Create virtual environment
echo ""
echo "🐍 Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Python dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  requirements.txt not found, installing core dependencies${NC}"
    pip install flask flask-cors requests aiohttp fastapi uvicorn
fi

# Install Node dependencies
echo ""
echo "📦 Installing Node.js dependencies..."
npm install
echo -e "${GREEN}✅ Node.js dependencies installed${NC}"

# Make scripts executable
echo ""
echo "🔧 Making scripts executable..."
chmod +x x-start 2>/dev/null || true
chmod +x x-stop 2>/dev/null || true
chmod +x aurora_chat_server.py 2>/dev/null || true
chmod +x install-linux.sh 2>/dev/null || true
echo -e "${GREEN}✅ Scripts are executable${NC}"

# Create systemd service files (optional)
echo ""
echo "🔧 Setting up systemd services (optional)..."
read -p "Do you want to install Aurora as a systemd service? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo tee /etc/systemd/system/aurora.service > /dev/null <<EOF
[Unit]
Description=Aurora-X AI System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/.venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$(pwd)/.venv/bin/python3 $(pwd)/x-start
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable aurora.service
    echo -e "${GREEN}✅ Systemd service installed${NC}"
    echo "   Start with: sudo systemctl start aurora"
    echo "   Stop with: sudo systemctl stop aurora"
    echo "   Status: sudo systemctl status aurora"
fi

# Test Aurora Core
echo ""
echo "🧪 Testing Aurora Core..."
if python3 -c "from aurora_core import create_aurora_core; print('✅ Aurora Core OK')" 2>/dev/null; then
    echo -e "${GREEN}✅ Aurora Core imports successfully${NC}"
else
    echo -e "${RED}❌ Aurora Core import failed${NC}"
    echo "   Check if aurora_core.py exists in the current directory"
    exit 1
fi

# Check ports availability
echo ""
echo "🔍 Checking port availability..."
PORTS=(5000 5001 5002 5003 5005 5173 9000)
for port in "${PORTS[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Port $port is already in use${NC}"
    else
        echo -e "${GREEN}✅ Port $port is available${NC}"
    fi
done

# Create startup helper script
echo ""
echo "🔧 Creating startup helper..."
cat > start-aurora.sh <<'STARTSCRIPT'
#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
python3 x-start
STARTSCRIPT
chmod +x start-aurora.sh

cat > stop-aurora.sh <<'STOPSCRIPT'
#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
python3 x-stop
STOPSCRIPT
chmod +x stop-aurora.sh

echo -e "${GREEN}✅ Helper scripts created${NC}"

# Installation complete
echo ""
echo "============================================"
echo -e "${GREEN}🎉 Aurora-X Installation Complete!${NC}"
echo "============================================"
echo ""
echo "📝 Next Steps:"
echo "   1. Activate virtual environment:"
echo "      source .venv/bin/activate"
echo ""
echo "   2. Start Aurora:"
echo "      ./start-aurora.sh"
echo "      OR"
echo "      python3 x-start"
echo ""
echo "   3. Access Aurora:"
echo "      🌐 Frontend:  http://localhost:5000"
echo "      💬 Chat:      http://localhost:5003"
echo "      📊 Dashboard: http://localhost:5005"
echo ""
echo "   4. Stop Aurora:"
echo "      ./stop-aurora.sh"
echo "      OR"
echo "      python3 x-stop"
echo ""
echo "🐛 Troubleshooting:"
echo "   • Check logs: tail -f aurora_*.log"
echo "   • Test services: curl http://localhost:5003/api/health"
echo "   • Port conflicts: sudo lsof -i :5003"
echo ""
echo "📚 Documentation:"
echo "   • Terminal commands: cat AURORA_TERMINAL_COMMANDS.md"
echo "   • Linux specific: cat LINUX_CHAT_FIX.md"
echo ""
echo "✨ Aurora is ready to learn and grow with you!"
