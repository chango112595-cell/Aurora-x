# Building the Aurora-X Workspace

## Quick Start

For impatient developers who want to get started immediately:

```bash
# Clone the repository
git clone https://github.com/chango112595-cell/Aurora-x.git
cd Aurora-x

# Install Python dependencies
pip install -e .

# Install Node.js dependencies
npm install

# Build the frontend
npm run build

# Run tests to verify
make test

# Start the dashboard
make serve-v3
```

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Requirements](#system-requirements)
3. [Installation Steps](#installation-steps)
4. [Building Components](#building-components)
5. [Running the Application](#running-the-application)
6. [Verification](#verification)
7. [Common Issues](#common-issues)
8. [Development Workflow](#development-workflow)

---

## Prerequisites

### Required Software

- **Python 3.8+** (Python 3.12.3 recommended)
- **Node.js 18+** (Node.js 20.19.5 recommended)
- **npm 8+** (npm 10.8.2 recommended)
- **Git** (for version control)

### Optional Tools

- **Make** (for using Makefile commands)
- **Docker** (for containerized deployment)
- **PostgreSQL** (for production database)

### Verify Installations

```bash
# Check Python version
python --version
# Expected: Python 3.8 or higher

# Check Node.js version
node --version
# Expected: v18.0.0 or higher

# Check npm version
npm --version
# Expected: 8.0.0 or higher

# Check Make
make --version
# Expected: GNU Make 3.81 or higher
```

---

## System Requirements

### Hardware

- **Minimum:**
  - 2 GB RAM
  - 1 GB free disk space
  - Dual-core CPU

- **Recommended:**
  - 4 GB+ RAM
  - 5 GB+ free disk space
  - Quad-core CPU

### Operating Systems

- ✅ Linux (Ubuntu 20.04+, Debian 10+, Fedora 35+)
- ✅ macOS (10.15+)
- ✅ Windows (10/11 with WSL2)

---

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/chango112595-cell/Aurora-x.git
cd Aurora-x
```

### 2. Set Up Python Environment

#### Option A: Using pip (Recommended)

```bash
# Install in editable mode
pip install -e .

# Or install from requirements.txt
pip install -r requirements.txt
```

#### Option B: Using Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -e .
```

#### Option C: Using uv (Fast Alternative)

```bash
# Install uv if not already installed
pip install uv

# Install dependencies
uv pip install -e .
```

### 3. Set Up Node.js Environment

```bash
# Install Node.js dependencies
npm install

# Or using package-lock.json for exact versions
npm ci
```

### 4. Configure Environment Variables

```bash
# Copy environment template
cp .env.template .env

# Edit .env file with your settings
# Required variables:
# - AURORA_PORT (default: 5001)
# - AURORA_SEED (optional: for reproducible runs)
# - DISCORD_WEBHOOK_URL (optional: for notifications)
```

Example `.env` file:
```bash
AURORA_PORT=5001
AURORA_SEED=42
AURORA_ORCH_INTERVAL=300
AURORA_GIT_AUTO=0
```

---

## Building Components

### Python Package

The Python package is built using setuptools and is defined in `pyproject.toml`.

```bash
# Install in development/editable mode
pip install -e .

# This creates the following command-line tools:
# - aurorax: Main synthesis engine CLI
# - aurorax-serve: Dashboard server
```

Verify installation:
```bash
# Check if aurorax is available
aurorax --help

# Check if aurorax-serve is available
aurorax-serve --help
```

### Frontend (React + Vite)

```bash
# Development build (with hot reload)
npm run dev

# Production build
npm run build

# The build output goes to the dist/ directory
```

### Backend Server (Node.js + Express)

```bash
# Type check
npm run check

# Build server
npm run build

# This bundles server code using esbuild
```

### Database Setup (Optional)

```bash
# Push database schema
npm run db:push

# This uses drizzle-kit to set up the database
```

---

## Running the Application

### Method 1: Using Make Commands (Recommended)

```bash
# View all available commands
make help

# Start the dashboard server
make serve-v3
# Access at: http://localhost:5001/dashboard

# Run the orchestrator (auto-monitors specs)
make orchestrator

# Run orchestrator in background
make orchestrate-bg

# Check system health
make health-check

# Run the synthesis engine with a spec
make spec3-all SPEC3=specs/check_palindrome.md
```

### Method 2: Direct Python Commands

```bash
# Run synthesis with a spec file
aurorax --spec-file ./specs/rich_spec.md --outdir runs

# Start the dashboard server
aurorax-serve

# Or using Python module syntax
python -m aurora_x.main --spec-file ./specs/rich_spec.md

# Start dashboard server
python -m aurora_x.serve
```

### Method 3: Using npm Scripts

```bash
# Development mode (with hot reload)
npm run dev

# Production mode
npm run start
```

### Method 4: Docker (Advanced)

```bash
# Build Docker image
docker build -f Dockerfile.app -t aurora-x:latest .

# Run container
docker run -p 5000:5000 -p 5001:5001 aurora-x:latest

# Or use docker-compose
docker-compose -f docker-compose.yml up
```

---

## Verification

### 1. Run Tests

```bash
# Run all tests using Make
make test

# Run tests using pytest directly
pytest -v

# Run with coverage
pytest --cov=aurora_x --cov-report=html

# Run specific test file
pytest tests/test_seeds.py -v

# Run security checks
make sec

# Run linter
make lint
```

### 2. Check Service Health

```bash
# Check all services
make health

# Check specific endpoints
curl http://localhost:5001/healthz
curl http://localhost:5000/api/health

# Check server status
make server-status
```

### 3. Verify Dashboard

```bash
# Start dashboard
make serve-v3

# Open in browser
make open-dashboard

# Or manually navigate to:
# http://localhost:5001/dashboard
```

### 4. Run Demo

```bash
# Check demo status
make demo-status

# Seed demo data
make demo-seed

# Run all demo cards
make demo-all

# List available demos
make demo-list

# Open demo dashboard
make open-demos
```

### 5. Test Synthesis Engine

```bash
# Run a simple synthesis test
aurorax --spec-file specs/check_palindrome.md --outdir runs

# Check the output
ls -la runs/

# View the latest run report
make open-report
```

---

## Common Issues

### Issue 1: Python Import Errors

**Problem:** `ModuleNotFoundError: No module named 'aurora_x'`

**Solution:**
```bash
# Ensure you installed in editable mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Issue 2: Port Already in Use

**Problem:** `Address already in use` when starting server

**Solution:**
```bash
# Kill process on port 5000
make server-fix

# Or manually
lsof -ti:5000 | xargs kill -9
lsof -ti:5001 | xargs kill -9

# Restart all services
make restart-all
```

### Issue 3: npm Install Fails

**Problem:** `npm ERR! peer dependency` errors

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install

# Or use legacy peer deps
npm install --legacy-peer-deps
```

### Issue 4: Permission Denied

**Problem:** `EACCES: permission denied` errors

**Solution:**
```bash
# Fix npm permissions (Linux/macOS)
sudo chown -R $(whoami) ~/.npm
sudo chown -R $(whoami) ./node_modules

# Or use npx instead of global install
npx <command>
```

### Issue 5: Database Connection Failed

**Problem:** Cannot connect to PostgreSQL

**Solution:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Or use SQLite for local development (default)
# Aurora-X uses SQLite by default for corpus storage
```

### Issue 6: TypeScript Compilation Errors

**Problem:** Type errors when running `npm run check`

**Solution:**
```bash
# Install TypeScript dependencies
npm install --save-dev typescript @types/node

# Run type check
npm run check

# If errors persist, check tsconfig.json
cat tsconfig.json
```

### Issue 7: Make Command Not Found

**Problem:** `make: command not found`

**Solution:**
```bash
# On Ubuntu/Debian
sudo apt-get install build-essential

# On macOS
xcode-select --install

# On Windows
# Use WSL2 or Git Bash, or run commands directly
```

---

## Development Workflow

### Daily Development

```bash
# 1. Pull latest changes
git pull origin main

# 2. Install/update dependencies
pip install -e .
npm install

# 3. Start development server
npm run dev

# 4. In another terminal, start orchestrator
make orchestrate-bg

# 5. Make your changes

# 6. Run tests
make test

# 7. Run linter
make lint

# 8. Commit changes
git add .
git commit -m "Your commit message"
git push
```

### Creating New Specs

```bash
# 1. Create spec file in specs/
cat > specs/my_function.md << 'EOF'
# SpecV3: My Function

def my_function(x: int) -> int

## Examples
my_function(5) -> 10
my_function(0) -> 0

## Post
assert my_function(x) >= 0
EOF

# 2. Compile spec
make spec3-all SPEC3=specs/my_function.md

# 3. Check output
ls -la runs/

# 4. View report
make open-report
```

### Running Continuous Learning

```bash
# Run self-learning mode
make self-learn

# Or with custom parameters
python -m aurora_x.self_learn --sleep 300 --max-iters 50 --beam 20
```

### Debugging

```bash
# Run full debug suite
make debug

# Check system health
make health-check

# View logs
tail -f /tmp/aurora_orch.log

# Check bridge service
bash scripts/bridge_autostart.sh
```

### Quality Gates

```bash
# Run all quality checks
make gates

# Individual checks
make lint     # Ruff linter
make sec      # Bandit security scanner
make cov      # Coverage report
```

---

## Advanced Topics

### Custom Configuration

Edit `.aurora/config.yml` to customize:
- Core settings (seed, max_iterations, timeout)
- Learning parameters (epsilon, decay, cooldown)
- Quality gates (drift limits, coverage thresholds)
- CI/CD settings

Example:
```yaml
# Aurora-X Configuration
version: 1.0
project: aurora-x

core:
  seed: 42
  max_iterations: 1000
  timeout: 300

learning:
  epsilon: 0.15
  decay: 0.98
  cooldown_iters: 5
  max_drift_per_iter: 0.1

quality_gates:
  max_corpus_drift: 0.15
  min_seed_coverage: 0.8
  max_regression_rate: 0.05
```

### Production Deployment

See `README_deploy.md` and `VPS_DEPLOYMENT_CHECKLIST.md` for detailed deployment instructions.

Quick production setup:
```bash
# Build for production
npm run build

# Set production environment
export NODE_ENV=production

# Start with production config
npm run start

# Or use Docker
docker-compose -f docker-compose.yml up -d
```

### Cloudflare Tunnel Setup

See `CLOUDFLARE_SETUP.md` for detailed instructions on setting up Cloudflare Tunnel for secure access.

```bash
# Quick tunnel start
./cloudflare-quick-tunnel.sh

# Or configure persistent tunnel
./setup-tunnel.sh
```

---

## Additional Resources

- **Main README**: `README.md` - Overview and quick start
- **Complete Documentation**: `COMPLETE_PROJECT_DOCUMENTATION.md` - Full project docs
- **API Documentation**: See individual README files for specific features
- **Troubleshooting**: `DEBUGGING_REPORT.md` - Common issues and solutions
- **Production Roadmap**: `AURORA_PRODUCTION_ROADMAP.md` - Future plans

---

## Getting Help

1. **Check Documentation**: Start with `README.md` and this guide
2. **Run Debug**: `make debug` to check system health
3. **View Logs**: Check `/tmp/aurora_orch.log` for orchestrator logs
4. **GitHub Issues**: Report bugs or request features
5. **Discord**: Set up webhook for status notifications

---

## Summary

You now have a complete Aurora-X workspace! Here's what you can do:

✅ **Synthesis**: Run `make spec3-all SPEC3=specs/your_spec.md`  
✅ **Dashboard**: Run `make serve-v3` and visit http://localhost:5001/dashboard  
✅ **Orchestrator**: Run `make orchestrate-bg` for auto-monitoring  
✅ **Tests**: Run `make test` to verify everything works  
✅ **Development**: Run `npm run dev` for frontend development  

Happy coding! 🚀
