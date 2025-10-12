#!/usr/bin/env bash
set -euo pipefail

# ----- install docker & compose (Ubuntu) -----
if ! command -v docker >/dev/null 2>&1; then
  sudo apt-get update -y
  sudo apt-get install -y ca-certificates curl gnupg
  sudo install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release; echo $VERSION_CODENAME) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
  sudo apt-get update -y
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi

# ----- clone your repo (if not present) -----
mkdir -p ~/aurora-x && cd ~/aurora-x
if [ ! -d app/.git ]; then
  rm -rf app
  git clone https://github.com/chango112595-cell/Aurora-x app
fi

# ----- build & start -----
docker compose -f docker-compose.aurora-x.yml build
docker compose -f docker-compose.aurora-x.yml up -d

echo
echo "Aurora-X is starting behind Cloudflare..."
echo "Check health:  docker compose -f docker-compose.aurora-x.yml logs -f aurora"
echo "CF tunnel:     docker compose -f docker-compose.aurora-x.yml logs -f cloudflared"