
#!/bin/bash
set -euo pipefail

echo "🔧 Aurora-X Workflow Fix & Enable Script"
echo "========================================"
echo ""

# Check if we're in a git repo
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not in a git repository"
    exit 1
fi

echo "1️⃣ Checking workflow syntax..."
python3 tools/check_workflows.py || {
    echo "⚠️  Some workflows have issues, continuing..."
}

echo ""
echo "2️⃣ Checking for required secrets..."
REQUIRED_SECRETS=(
    "AURORA_GH_TOKEN"
    "DEPLOY_SSH_HOST"
    "DEPLOY_SSH_USER"
    "DEPLOY_SSH_KEY"
)

MISSING_SECRETS=()
for secret in "${REQUIRED_SECRETS[@]}"; do
    if ! gh secret list 2>/dev/null | grep -q "^$secret"; then
        MISSING_SECRETS+=("$secret")
    fi
done

if [ ${#MISSING_SECRETS[@]} -gt 0 ]; then
    echo "⚠️  Missing secrets (deployment workflows will fail):"
    for secret in "${MISSING_SECRETS[@]}"; do
        echo "   - $secret"
    done
    echo ""
    echo "ℹ️  Add secrets via: gh secret set SECRET_NAME"
else
    echo "✅ All required secrets configured"
fi

echo ""
echo "3️⃣ Workflow Status Summary:"
make workflow-status

echo ""
echo "4️⃣ Testing a sample workflow..."
if timeout 3 gh auth status > /dev/null 2>&1; then
    echo "✅ GitHub CLI connected successfully"
    gh workflow list | head -5 || echo "⚠️  Could not list workflows"
else
    echo "⚠️  GitHub CLI not authenticated or not installed"
    echo "   Skipping workflow listing (not required for syntax validation)"
fi

echo ""
echo "✅ Workflow check complete!"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff .github/workflows/"
echo "  2. Commit changes: git add .github/workflows && git commit -m 'Enable and fix workflows'"
echo "  3. Push changes: git push origin main"
echo "  4. Monitor: gh run list --limit 5"
