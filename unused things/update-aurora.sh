#!/usr/bin/env bash
# Aurora-X Auto Updater
# This script checks for git updates, pulls changes, and rebuilds/restarts the Docker container

set -Eeuo pipefail

# Get the root directory of the project
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$ROOT_DIR"

# Load environment variables from .env file if it exists
if [[ -f .env ]]; then
    set -a
    source .env
    set +a
fi

# Configuration with defaults
: "${AURORA_GIT_URL:=}"                    # Optional: git repository URL
: "${AURORA_GIT_BRANCH:=main}"            # Default branch to track
: "${AURORA_HEALTH_TOKEN:=ok}"            # Health check token
: "${AURORA_DISCORD_WEBHOOK:=}"           # Optional Discord webhook URL
: "${GITHUB_REPOSITORY:=yourusername/aurora-x}"  # GitHub repository for Docker image

# Docker compose command
COMPOSE="docker compose -f docker-compose.yml"
HEALTH_URL="http://localhost:8000/healthz?token=${AURORA_HEALTH_TOKEN}"

# Function to send notifications
notify() {
    local msg="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [AURORA-UPDATER] $msg"
    
    # Send Discord notification if webhook is configured
    if [[ -n "$AURORA_DISCORD_WEBHOOK" ]]; then
        curl -fsSL -X POST -H "Content-Type: application/json" \
            -d "{\"content\":\"🔄 **Aurora-X Update** [${timestamp}]\\n${msg}\"}" \
            "$AURORA_DISCORD_WEBHOOK" >/dev/null 2>&1 || true
    fi
}

# Function to check if we're in a git repository
check_git_repo() {
    if [[ ! -d .git ]]; then
        if [[ -z "${AURORA_GIT_URL}" ]]; then
            notify "⚠️ Not in a git repository and AURORA_GIT_URL not set. Skipping update check."
            exit 0
        fi
        
        notify "📥 Initializing git repository with ${AURORA_GIT_URL}..."
        git init
        git remote add origin "$AURORA_GIT_URL"
        git fetch origin "$AURORA_GIT_BRANCH"
        git checkout -b "$AURORA_GIT_BRANCH" "origin/${AURORA_GIT_BRANCH}"
        notify "✅ Git repository initialized successfully"
    fi
}

# Main update process
main() {
    notify "🔍 Starting Aurora-X update check..."
    
    # Ensure we're in a git repository
    check_git_repo
    
    # Configure remote URL if provided
    if [[ -n "${AURORA_GIT_URL}" ]] && [[ -d .git ]]; then
        current_remote=$(git remote get-url origin 2>/dev/null || echo "")
        if [[ "$current_remote" != "$AURORA_GIT_URL" ]]; then
            notify "📝 Updating git remote URL to: $AURORA_GIT_URL"
            git remote set-url origin "$AURORA_GIT_URL"
        fi
    fi
    
    # Fetch latest changes
    notify "📡 Fetching latest changes from origin/${AURORA_GIT_BRANCH}..."
    git fetch origin "$AURORA_GIT_BRANCH" --quiet
    
    # Get current and remote SHA
    LOCAL_SHA="$(git rev-parse HEAD 2>/dev/null || echo 'none')"
    REMOTE_SHA="$(git rev-parse "origin/${AURORA_GIT_BRANCH}" 2>/dev/null || echo 'none')"
    
    # Check if updates are available
    if [[ "$LOCAL_SHA" == "$REMOTE_SHA" ]]; then
        notify "✅ Already up-to-date (SHA: ${LOCAL_SHA:0:8})"
        exit 0
    fi
    
    notify "📦 Updates available: ${LOCAL_SHA:0:8} → ${REMOTE_SHA:0:8}"
    
    # Pull the latest changes
    notify "⬇️ Pulling latest changes..."
    git reset --hard "origin/${AURORA_GIT_BRANCH}"
    
    # Get the latest commit message
    COMMIT_MSG=$(git log -1 --pretty=format:"%s" 2>/dev/null || echo "No commit message")
    notify "📝 Latest commit: ${COMMIT_MSG}"
    
    # Rebuild and restart the Aurora container
    notify "🔨 Rebuilding Aurora-X Docker image..."
    $COMPOSE build --pull aurora
    
    notify "🚀 Restarting Aurora-X container..."
    $COMPOSE up -d aurora
    
    # Wait for the service to be healthy
    notify "⏳ Waiting for Aurora-X to be healthy..."
    
    MAX_ATTEMPTS=30
    ATTEMPT=0
    
    while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
        ATTEMPT=$((ATTEMPT + 1))
        
        if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
            notify "✅ Aurora-X is healthy and running! (Attempt ${ATTEMPT}/${MAX_ATTEMPTS})"
            
            # Get container status
            CONTAINER_STATUS=$($COMPOSE ps aurora --format json 2>/dev/null | jq -r '.Status' 2>/dev/null || echo "unknown")
            notify "📊 Container status: ${CONTAINER_STATUS}"
            
            notify "🎉 Update completed successfully!"
            exit 0
        fi
        
        if [ $ATTEMPT -eq 10 ] || [ $ATTEMPT -eq 20 ]; then
            notify "⏳ Still waiting for health check... (Attempt ${ATTEMPT}/${MAX_ATTEMPTS})"
        fi
        
        sleep 2
    done
    
    # Health check failed
    notify "❌ Health check failed after ${MAX_ATTEMPTS} attempts!"
    notify "📋 Checking container logs..."
    
    # Get last few lines of logs
    LOGS=$($COMPOSE logs --tail=10 aurora 2>&1 || echo "Could not retrieve logs")
    notify "📜 Recent logs: ${LOGS}"
    
    notify "⚠️ Please check the container manually: docker compose logs -f aurora"
    exit 1
}

# Run the main function
main "$@"