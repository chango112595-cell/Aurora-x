
#!/usr/bin/env bash
set -euo pipefail

echo "🔍 Diagnosing Git Configuration..."
echo ""

# Check git config
echo "Current Git Config:"
git config --list | grep -E '(user|remote)' || echo "  No git config found"
echo ""

# Check remote
echo "Current Remote:"
git remote -v || echo "  No remote configured"
echo ""

# Check environment variables
echo "Environment Variables:"
echo "  AURORA_GIT_URL=${AURORA_GIT_URL:-NOT SET}"
echo "  AURORA_GH_TOKEN=${AURORA_GH_TOKEN:+SET (hidden)}"
echo ""

# Fix git identity
if [ -z "$(git config user.email 2>/dev/null || true)" ]; then
  echo "⚠️  Git user.email not set"
  git config user.email "aurora@local"
  echo "✅ Set git user.email to aurora@local"
fi

if [ -z "$(git config user.name 2>/dev/null || true)" ]; then
  echo "⚠️  Git user.name not set"
  git config user.name "Aurora X"
  echo "✅ Set git user.name to Aurora X"
fi

# Check remote URL
REMOTE_URL=$(git config remote.origin.url 2>/dev/null || true)
if [ -z "$REMOTE_URL" ]; then
  echo "⚠️  No remote origin configured"
  if [ -n "${AURORA_GIT_URL:-}" ]; then
    git remote add origin "$AURORA_GIT_URL"
    echo "✅ Added remote origin: $AURORA_GIT_URL"
  else
    echo "❌ AURORA_GIT_URL not set - cannot configure remote"
  fi
fi

echo ""
echo "🔍 Testing Git Operations..."

# Test fetch
if git fetch origin 2>&1 | head -5; then
  echo "✅ Git fetch successful"
else
  echo "❌ Git fetch failed - check credentials and remote URL"
fi

echo ""
echo "Final Status:"
git status
