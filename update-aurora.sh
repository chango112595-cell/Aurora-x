#!/usr/bin/env bash
# Aurora-X Auto Updater
set -Eeuo pipefail

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$ROOT_DIR"

# ---- Config from .env (already used by your stack) ----
: "${AURORA_GIT_URL:=}"            # optional: if set, overrides current remote
: "${AURORA_GIT_BRANCH:=main}"
: "${AURORA_HEALTH_TOKEN:=ok}"
: "${AURORA_DISCORD_WEBHOOK:=}"    # optional

COMPOSE="docker compose -f docker-compose.aurora-x.yml"
HEALTH_URL="http://localhost:8000/healthz?token=${AURORA_HEALTH_TOKEN}"

notify() {
  local msg="$1"
  echo "[UPDATER] $msg"
  if [[ -n "$AURORA_DISCORD_WEBHOOK" ]]; then
    curl -fsSL -X POST -H "Content-Type: application/json" \
      -d "{\"content\":\"$msg\"}" \
      "$AURORA_DISCORD_WEBHOOK" >/dev/null || true
  fi
}

# 1) Ensure app exists (the setup script clones it into ./app)
if [[ ! -d app/.git ]]; then
  notify "No git repo found in ./app — attempting initial clone…"
  if [[ -z "${AURORA_GIT_URL}" ]]; then
    notify "AURORA_GIT_URL not set. Skipping."
    exit 0
  fi
  rm -rf app
  git clone --branch "$AURORA_GIT_BRANCH" "$AURORA_GIT_URL" app
fi

# 2) Fetch latest & decide if there are changes
pushd app >/dev/null
if [[ -n "${AURORA_GIT_URL}" ]]; then
  git remote set-url origin "$AURORA_GIT_URL" || true
fi

git fetch origin "$AURORA_GIT_BRANCH"
LOCAL_SHA="$(git rev-parse HEAD)"
REMOTE_SHA="$(git rev-parse "origin/${AURORA_GIT_BRANCH}")"

if [[ "$LOCAL_SHA" == "$REMOTE_SHA" ]]; then
  notify "No updates (HEAD=$LOCAL_SHA)."
  popd >/dev/null
  exit 0
fi

notify "Updates found: $LOCAL_SHA -> $REMOTE_SHA. Pulling…"
git reset --hard "origin/${AURORA_GIT_BRANCH}"
popd >/dev/null

# 3) Rebuild + restart the aurora service only
notify "Rebuilding image and restarting service…"
$COMPOSE build --pull aurora
$COMPOSE up -d aurora

# 4) Health check
notify "Waiting for health check…"
for i in {1..20}; do
  if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
    notify "Aurora healthy ✅"
    exit 0
  fi
  sleep 2
done

notify "Health check failed ❌ — check logs: \`docker compose logs -f aurora\`"
exit 1