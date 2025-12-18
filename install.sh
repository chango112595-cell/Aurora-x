#!/bin/bash
# ============================================================================
# Aurora-X Ultra - Universal Installation Script
# This script sets up the complete Aurora-X environment on any Linux/macOS system
# ============================================================================

set -e

echo "============================================================"
echo "  AURORA-X ULTRA - UNIVERSAL INSTALLER"
echo "  AI-Powered Autonomous Code Synthesis Platform"
echo "============================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${CYAN}[i]${NC} $1"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if command -v apt-get &> /dev/null; then
            PKG_MANAGER="apt"
        elif command -v yum &> /dev/null; then
            PKG_MANAGER="yum"
        elif command -v dnf &> /dev/null; then
            PKG_MANAGER="dnf"
        elif command -v pacman &> /dev/null; then
            PKG_MANAGER="pacman"
        else
            PKG_MANAGER="unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        PKG_MANAGER="brew"
    else
        OS="unknown"
        PKG_MANAGER="unknown"
    fi
    print_info "Detected OS: $OS (Package Manager: $PKG_MANAGER)"
}

# Check for required commands
check_requirements() {
    echo ""
    echo "Checking system requirements..."
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_status "Python 3 found: $PYTHON_VERSION"
    else
        print_error "Python 3 not found. Please install Python 3.11+"
        exit 1
    fi
    
    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_status "Node.js found: $NODE_VERSION"
    else
        print_warning "Node.js not found. Will attempt to install..."
        NEED_NODE=true
    fi
    
    # Check npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        print_status "npm found: $NPM_VERSION"
    else
        print_warning "npm not found. Will be installed with Node.js..."
    fi
    
    # Check pip
    if command -v pip3 &> /dev/null; then
        print_status "pip3 found"
    else
        print_warning "pip3 not found. Will attempt to install..."
        NEED_PIP=true
    fi
}

# Install system dependencies
install_system_deps() {
    echo ""
    echo "Installing system dependencies..."
    
    case $PKG_MANAGER in
        apt)
            sudo apt-get update -qq
            sudo apt-get install -y -qq python3-pip python3-venv build-essential curl git
            if [ "$NEED_NODE" = true ]; then
                curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
                sudo apt-get install -y nodejs
            fi
            ;;
        yum|dnf)
            sudo $PKG_MANAGER install -y python3-pip python3-devel gcc gcc-c++ make curl git
            if [ "$NEED_NODE" = true ]; then
                curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
                sudo $PKG_MANAGER install -y nodejs
            fi
            ;;
        pacman)
            sudo pacman -Syu --noconfirm python-pip base-devel curl git
            if [ "$NEED_NODE" = true ]; then
                sudo pacman -S --noconfirm nodejs npm
            fi
            ;;
        brew)
            brew update
            brew install python3 curl git
            if [ "$NEED_NODE" = true ]; then
                brew install node
            fi
            ;;
        *)
            print_warning "Unknown package manager. Please install dependencies manually:"
            echo "  - Python 3.11+"
            echo "  - Node.js 18+"
            echo "  - npm"
            echo "  - git"
            echo "  - build-essential (or equivalent)"
            ;;
    esac
    
    print_status "System dependencies installed"
}

# Setup Python virtual environment
setup_python_env() {
    echo ""
    echo "Setting up Python environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Created Python virtual environment"
    else
        print_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip -q
    
    # Install Python dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt -q
        print_status "Installed Python dependencies from requirements.txt"
    fi
    
    # Install the aurora-x package in editable mode
    if [ -f "pyproject.toml" ]; then
        pip install -e . -q
        print_status "Installed aurora-x package"
    fi
    
    print_status "Python environment ready"
}

# Setup Node.js environment
setup_node_env() {
    echo ""
    echo "Setting up Node.js environment..."
    
    if [ -f "package.json" ]; then
        npm install
        print_status "Installed Node.js dependencies"
    else
        print_warning "No package.json found"
    fi
    
    print_status "Node.js environment ready"
}

# Create necessary directories
create_directories() {
    echo ""
    echo "Creating necessary directories..."
    
    mkdir -p data/memory/projects
    mkdir -p logs
    mkdir -p runs
    mkdir -p specs/requests
    mkdir -p .aurora_knowledge
    
    print_status "Directories created"
}

# Setup environment variables
setup_env() {
    echo ""
    echo "Setting up environment variables..."
    
    if [ ! -f ".env" ]; then
        cat > .env << 'EOF'
# Aurora-X Ultra Environment Configuration
# Copy this file to .env and customize as needed

# Server Ports
AURORA_PORT=5000
AURORA_NEXUS_PORT=5002
LUMINAR_PORT=8000

# Mode Settings
AURORA_MODE=offline
NODE_ENV=development

# Feature Flags
AURORA_HYPERSPEED=1
AURORA_SELF_HEAL=1
AURORA_AUTONOMOUS=1
EOF
        print_status "Created .env file with default settings"
    else
        print_info ".env file already exists"
    fi
}

# Build the application
build_app() {
    echo ""
    echo "Building application..."
    
    # Build frontend if needed
    if [ -f "package.json" ] && grep -q '"build"' package.json; then
        npm run build 2>/dev/null || print_warning "Build step skipped (dev mode)"
    fi
    
    print_status "Application built"
}

# Print final instructions
print_final_instructions() {
    echo ""
    echo "============================================================"
    echo -e "${GREEN}  AURORA-X ULTRA INSTALLATION COMPLETE${NC}"
    echo "============================================================"
    echo ""
    echo "To start Aurora-X Ultra:"
    echo ""
    echo "  Option 1 - Quick Start (All services):"
    echo "    ./aurora-start"
    echo ""
    echo "  Option 2 - Using Make:"
    echo "    make start-all"
    echo ""
    echo "  Option 3 - Individual services:"
    echo "    make web          # Start web application (port 5000)"
    echo "    make nexus        # Start Aurora Nexus V3 (port 5002)"
    echo "    make luminar      # Start Luminar Nexus V2 (port 8000)"
    echo ""
    echo "Other useful commands:"
    echo "    make help         # Show all available commands"
    echo "    make status       # Check system status"
    echo "    make test         # Run tests"
    echo ""
    echo "Access the application at:"
    echo "    http://localhost:5000"
    echo ""
    echo "============================================================"
    echo -e "${PURPLE}  Aurora-X Ultra v3.1.0 - Peak Autonomy${NC}"
    echo "  188 Tiers | 66 AEMs | 550 Modules | 300 Workers"
    echo "============================================================"
}

# Main installation flow
main() {
    detect_os
    check_requirements
    
    # Ask before installing system deps
    if [ "$NEED_NODE" = true ] || [ "$NEED_PIP" = true ]; then
        read -p "Install missing system dependencies? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_system_deps
        fi
    fi
    
    create_directories
    setup_python_env
    setup_node_env
    setup_env
    build_app
    print_final_instructions
}

# Run main installation
main "$@"
