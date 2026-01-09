#!/usr/bin/env bash
# Aurora-X Release Script
# Automates version tagging and release creation

set -euo pipefail

VERSION="${1:-}"
MESSAGE="${2:-}"

if [ -z "$VERSION" ]; then
    echo "Usage: ./scripts/release.sh <version> [message]"
    echo "Example: ./scripts/release.sh v0.1.1 'Bug fixes and improvements'"
    exit 1
fi

# Validate version format (semver)
if ! echo "$VERSION" | grep -qE '^v[0-9]+\.[0-9]+\.[0-9]+$'; then
    echo "Error: Version must follow semver format (e.g., v0.1.1)"
    exit 1
fi

# Default message if not provided
if [ -z "$MESSAGE" ]; then
    MESSAGE="Aurora X $VERSION - $(date +%Y-%m-%d)"
fi

echo "🚀 Creating release $VERSION..."
echo "Message: $MESSAGE"
echo ""

# Ensure we're on main and up to date
git checkout main
git pull origin main

# Check if tag already exists
if git rev-parse "$VERSION" >/dev/null 2>&1; then
    echo "Error: Tag $VERSION already exists"
    exit 1
fi

# Create and push tag
echo "📝 Creating tag..."
git tag -a "$VERSION" -m "$MESSAGE"
git push origin "$VERSION"

echo ""
echo "✅ Tag $VERSION pushed successfully"
echo ""
echo "📦 Docker image will be built automatically:"
echo "   ghcr.io/chango112595-cell/Aurora-x:$VERSION"
echo ""
echo "🔍 Verify workflow:"
echo "   gh run list --workflow 'docker-release.yml' --limit 1"
echo ""
echo "📋 Check release:"
echo "   gh release view $VERSION"
echo ""
