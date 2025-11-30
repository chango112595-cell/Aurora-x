#!/usr/bin/env bash
# installers/install-universal.sh
# Universal bootstrap installer for Aurora (Linux/macOS). Detects arch, offers Docker or native install.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "Aurora Universal Installer (root=$ROOT)"

OS="$(uname -s)"
ARCH="$(uname -m)"
echo "Detected OS=$OS ARCH=$ARCH"

usage(){
  cat <<EOF
Usage: $0 [--mode docker|native] [--service systemd|launchd|nssm] [--token YOUR_TOKEN]
Examples:
  $0 --mode docker
  $0 --mode native --service systemd --token supersecret
EOF
  exit 1
}

MODE="docker"
SERVICE=""
TOKEN="${AURORA_API_TOKEN:-aurora-dev-token}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="$2"; shift 2 ;;
    --service) SERVICE="$2"; shift 2 ;;
    --token) TOKEN="$2"; shift 2 ;;
    -h|--help) usage ;;
    *) echo "Unknown arg $1"; usage ;;
  esac
done

echo "Install mode: $MODE"
export AURORA_API_TOKEN="$TOKEN"

if [[ "$MODE" == "docker" ]]; then
  if ! command -v docker >/dev/null 2>&1; then
    echo "Docker not found. Please install Docker first."
    exit 1
  fi
  echo "Building multi-arch image (local)..."
  if docker buildx version >/dev/null 2>&1; then
    bash "$ROOT/docker/buildx-build.sh"
  else
    docker build -t auroraos:latest -f "$ROOT/docker/Dockerfile.multi" "$ROOT"
  fi
  echo "Docker image built: auroraos:latest"
  cat <<EOF
Run with:
  docker run -it --rm -p 5000:5000 -p 9701:9701 -v $ROOT:/app auroraos:latest
EOF
  exit 0
fi

if [[ "$MODE" == "native" ]]; then
  echo "Performing native install (Python venv + node if present)..."

  # python
  if ! command -v python3 >/dev/null 2>&1; then
    echo "Python3 is required. Please install python3."
    exit 1
  fi

  PYTHON=python3
  $PYTHON -m venv "$ROOT/.venv"
  source "$ROOT/.venv/bin/activate"
  pip install --upgrade pip
  pip install fastapi uvicorn[standard] psutil watchdog requests

  # Node (optional)
  if command -v npm >/dev/null 2>&1; then
    echo "Installing node deps..."
    npm install --prefix "$ROOT" || true
    if ! command -v tsx >/dev/null 2>&1; then
      npm i -g tsx
    fi
  fi

  mkdir -p "$ROOT/aurora_logs" "$ROOT/.aurora/pids"
  echo "$TOKEN" > "$ROOT/.aurora/api.token"

  echo "Native install complete. Start with ./aurora.sh start"
  if [[ "$SERVICE" == "systemd" ]]; then
    echo "Installing systemd service..."
    sudo cp "$ROOT/packaging/aurora.service" /etc/systemd/system/aurora.service
    sudo systemctl daemon-reload
    sudo systemctl enable --now aurora.service
    echo "Systemd service installed & started."
  fi

  exit 0
fi

echo "Unknown mode"
usage
