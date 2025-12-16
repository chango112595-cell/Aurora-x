# Aurora-X Ultra - Porting & Installation Guide

This document explains how to install Aurora-X Ultra on a new system.

## Prerequisites

Before installing, ensure you have:

| Requirement | Minimum Version | Recommended |
|------------|-----------------|-------------|
| Python | 3.8+ | 3.11+ |
| Node.js | 18+ | 20+ |
| npm | 8+ | 10+ |
| RAM | 4GB | 8GB+ |
| Disk | 2GB | 5GB+ |

## Quick Installation

### Option 1: Automated Install (Recommended)

```bash
# Make the install script executable
chmod +x install.sh

# Run the installer
./install.sh
```

### Option 2: Using Make

```bash
# Install everything
make install-all

# Or step by step:
make install-python   # Setup Python environment
make install-node     # Setup Node.js environment
make install-deps     # Install all dependencies
```

### Option 3: Manual Installation

```bash
# 1. Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install Python dependencies
pip install -r requirements.txt
pip install -e .

# 3. Install Node.js dependencies
npm install

# 4. Create necessary directories
mkdir -p data/memory/projects logs runs specs/requests
```

## Starting Aurora-X

### All Services (Recommended)

```bash
./aurora-start
# OR
make start-all
```

### Individual Services

| Service | Command | Port |
|---------|---------|------|
| Web Application | `make web` or `npm run dev` | 5000 |
| Aurora Nexus V3 | `make nexus` or `python3 aurora_nexus_v3/main.py` | 5002 |
| Luminar Nexus V2 | `make luminar` or `python3 tools/luminar_nexus_v2.py serve` | 8000 |

## Project Structure

```
Aurora-X/
├── install.sh              # Universal installer script
├── requirements.txt        # Python dependencies
├── package.json            # Node.js dependencies
├── pyproject.toml          # Python package config
├── Makefile                # Build automation
│
├── aurora_nexus_v3/        # Universal Consciousness System
│   ├── main.py             # Entry point
│   ├── core/               # Core modules
│   └── workers/            # 300 Autonomous Workers
│
├── tools/
│   └── luminar_nexus_v2.py # Chat + ML pattern learning
│
├── manifests/              # System manifests
│   ├── tiers.manifest.json        # 188 Grandmaster Tiers
│   ├── executions.manifest.json   # 66 Advanced Execution Methods
│   └── modules.manifest.json      # 550 Cross-Temporal Modules
│
├── client/                 # React Frontend
├── server/                 # Express Backend
└── shared/                 # Shared TypeScript types
```

## Configuration

### Environment Variables

Create a `.env` file (or copy from `.env.example`):

```bash
# Server Ports
AURORA_PORT=5000
AURORA_NEXUS_PORT=5002
LUMINAR_PORT=8000

# Mode Settings
AURORA_MODE=offline     # 'offline' or 'cloud'
NODE_ENV=development

# Feature Flags
AURORA_HYPERSPEED=1     # Enable hyperspeed mode
AURORA_SELF_HEAL=1      # Enable self-healing
AURORA_AUTONOMOUS=1     # Enable autonomous workers
```

### Database

Aurora-X uses SQLite by default for local storage. For production, configure PostgreSQL:

```bash
DATABASE_URL=postgresql://user:pass@host:5432/aurora
```

## Verification

After installation, verify the system:

```bash
# Check system status
make status

# Test Aurora Nexus
python3 aurora_nexus_v3/test_nexus.py

# Run all tests
make test
```

## Creating a Portable Package

To create a distributable archive:

```bash
make package
```

This creates `aurora-x-ultra-vX.X.X.tar.gz` containing:
- All source code
- Configuration files
- Manifests
- Install scripts
- Documentation

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   make kill-ports
   # Or manually: kill -9 $(lsof -t -i:5000)
   ```

2. **Python dependencies fail**
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

3. **Node modules corrupted**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Permission denied**
   ```bash
   chmod +x aurora-start install.sh
   ```

### Getting Help

- Check logs: `logs/` directory
- System health: `make health`
- Debug mode: `make debug`

## System Capabilities

Once installed, Aurora-X Ultra provides:

| Feature | Specification |
|---------|---------------|
| Intelligence Tiers | 188 Grandmaster Tiers |
| Execution Methods | 66 Advanced Execution Methods |
| Cross-Temporal Modules | 550 Modules |
| Autonomous Workers | 300 Non-conscious Workers |
| Hyperspeed Mode | 1000+ code units in <0.001s |
| Self-Healing | Automatic issue detection & repair |

## License

Aurora-X Ultra - AI-Powered Autonomous Code Synthesis Platform
