# Aurora-X Installation Guide

## 🚀 Installation Methods

Aurora-X can be installed and deployed in multiple ways depending on your environment and needs.

## 1. Docker (Recommended for Production)

### Quick Start with Docker Compose

```bash
# Standard deployment
export AURORA_TOKEN_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))')
docker compose up -d

# Production deployment (with resource limits)
docker compose -f compose.prod.yaml up -d
```

### Docker Image from GHCR

```bash
# Pull latest image
docker pull ghcr.io/chango112595-cell/Aurora-x:latest

# Or specific version
docker pull ghcr.io/chango112595-cell/Aurora-x:v0.1.0

# Run container
docker run -d \
  --name aurora-x \
  -p 8000:8000 \
  -e AURORA_TOKEN_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))') \
  ghcr.io/chango112595-cell/Aurora-x:latest
```

**Platforms Supported:**
- ✅ Linux (amd64, arm64)
- ✅ macOS (amd64, arm64 via Docker Desktop)
- ✅ Windows (via Docker Desktop)

## 2. Kubernetes

### Using Existing Manifests

```bash
# Apply deployment
kubectl apply -f k8s/aurora-deployment.yaml

# Or use Helm
helm install aurora-x ./k8s/helm/aurora-x

# Or use Kustomize
kubectl apply -k ./k8s/kustomize/base
```

### Update Image Version

```bash
kubectl set image deploy/aurora-x api=ghcr.io/chango112595-cell/Aurora-x:v0.1.0
kubectl rollout status deploy/aurora-x
```

**Platforms Supported:**
- ✅ Any Kubernetes cluster (1.20+)
- ✅ Cloud providers (AWS EKS, GKE, AKS)
- ✅ On-premises Kubernetes

## 3. Python Package (pip install)

### Install from Source

```bash
# Clone repository
git clone https://github.com/chango112595-cell/Aurora-x.git
cd Aurora-x

# Install in development mode
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

### Install from PyPI (if published)

```bash
pip install aurora-x
```

**Platforms Supported:**
- ✅ Linux (all distributions)
- ✅ macOS (Intel & Apple Silicon)
- ✅ Windows (via WSL or native)
- ✅ Python 3.8+ (3.11+ recommended)

## 4. Native Installation (Linux/macOS/Windows)

### Automated Installer

```bash
# Linux/macOS
chmod +x install.sh
./install.sh

# Or use Make
make install-all
```

### Manual Installation

```bash
# 1. Python environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .

# 2. Node.js (if needed)
npm install

# 3. Run
AURORA_TOKEN_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))') \
  uvicorn aurora_x.serve:app --host 0.0.0.0 --port 8000
```

**Platforms Supported:**
- ✅ Linux (Ubuntu, Debian, RHEL, etc.)
- ✅ macOS (Intel & Apple Silicon)
- ✅ Windows (native or WSL)

## 5. System Packages (Future)

### Debian/Ubuntu (.deb)

```bash
# Build package
bash installers/linux/create-deb.sh 1.0.0 amd64

# Install
sudo dpkg -i aurora-x_1.0.0_amd64.deb
```

### RPM (RHEL/CentOS)

```bash
# Build package
bash installers/linux/create-rpm.sh 1.0.0 x86_64

# Install
sudo rpm -i aurora-x-1.0.0-1.x86_64.rpm
```

### macOS Package

```bash
# Build package
bash installers/macos/create-pkg.sh

# Install
open aurora-x.pkg
```

### Windows MSI

```powershell
# Requires WiX Toolset
candle.exe Product.wxs
light.exe Product.wixobj -o Aurora-X.msi

# Install
msiexec /i Aurora-X.msi
```

## 6. Cloud Platforms

### AWS (ECS/Fargate)

```bash
# Use Docker image from GHCR
# Configure in ECS task definition
# Image: ghcr.io/chango112595-cell/Aurora-x:latest
```

### Google Cloud (Cloud Run)

```bash
# Deploy to Cloud Run
gcloud run deploy aurora-x \
  --image ghcr.io/chango112595-cell/Aurora-x:latest \
  --set-env-vars AURORA_TOKEN_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))')
```

### Azure (Container Instances)

```bash
# Deploy to Azure
az container create \
  --resource-group myResourceGroup \
  --name aurora-x \
  --image ghcr.io/chango112595-cell/Aurora-x:latest \
  --environment-variables AURORA_TOKEN_SECRET=<your-secret>
```

### Fly.io

```bash
# Deploy to Fly.io
flyctl launch --image ghcr.io/chango112595-cell/Aurora-x:latest
flyctl secrets set AURORA_TOKEN_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))')
```

### Render

```yaml
# render.yaml
services:
  - type: web
    name: aurora-x
    dockerfilePath: ./Dockerfile.api
    envVars:
      - key: AURORA_TOKEN_SECRET
        sync: false
```

## 7. Development Installation

### Local Development

```bash
# Clone and setup
git clone https://github.com/chango112595-cell/Aurora-x.git
cd Aurora-x

# Install with dev dependencies
pip install -e ".[dev]"

# Run with hot reload
make run
# OR
AURORA_TOKEN_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))') \
  uvicorn aurora_x.serve:app --reload
```

## Platform Compatibility Matrix

| Method | Linux | macOS | Windows | Cloud | K8s |
|--------|-------|-------|---------|-------|-----|
| Docker | ✅ | ✅ | ✅ | ✅ | ✅ |
| Docker Compose | ✅ | ✅ | ✅ | ✅ | N/A |
| Kubernetes | ✅ | ✅ | ✅ | ✅ | ✅ |
| pip install | ✅ | ✅ | ✅ | ✅ | ✅ |
| Native | ✅ | ✅ | ✅ | N/A | N/A |
| System Packages | ✅ | ✅ | ✅ | N/A | N/A |

## Requirements

### Minimum Requirements

- **Python**: 3.8+ (3.11+ recommended)
- **RAM**: 512MB (2GB recommended)
- **Disk**: 500MB (2GB recommended)
- **OS**: Linux, macOS, or Windows

### For Docker

- Docker 20.10+
- Docker Compose 2.0+ (optional)

### For Kubernetes

- Kubernetes 1.20+
- kubectl configured

## Quick Start by Platform

### Linux

```bash
# Option 1: Docker (easiest)
docker compose up -d

# Option 2: Native
pip install -e . && uvicorn aurora_x.serve:app
```

### macOS

```bash
# Option 1: Docker Desktop
docker compose up -d

# Option 2: Native
pip install -e . && uvicorn aurora_x.serve:app
```

### Windows

```powershell
# Option 1: Docker Desktop
docker compose up -d

# Option 2: WSL
wsl
pip install -e . && uvicorn aurora_x.serve:app

# Option 3: Native (PowerShell)
pip install -e .
$env:AURORA_TOKEN_SECRET = (python -c 'import secrets; print(secrets.token_hex(32))')
uvicorn aurora_x.serve:app
```

## Verification

After installation, verify it's working:

```bash
# Health check
curl http://127.0.0.1:8000/healthz

# Expected response
{"status":"ok","ok":true,...}
```

## Next Steps

- See [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) for production setup
- See [OPERATIONS.md](OPERATIONS.md) for operations guide
- See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup

---

**Status**: ✅ Aurora-X can be installed on **all major platforms** via multiple methods!
