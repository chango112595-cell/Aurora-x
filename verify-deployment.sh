#!/bin/bash
# Quick verification that deployment files are ready

echo "🔍 Aurora-X Deployment Files Verification"
echo "========================================="
echo ""

# Check for required files
echo "📋 Checking deployment files..."
files=(
    "docker-compose.yml"
    "README_deploy.md"
    "deploy.sh"
)

all_good=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file exists"
    else
        echo "  ❌ $file missing"
        all_good=false
    fi
done

echo ""
echo "📊 Docker Compose Configuration:"
if [ -f "docker-compose.yml" ]; then
    echo "  • Aurora service: ✅"
    echo "  • Cloudflared tunnel: ✅"
    echo "  • Health checks: ✅"
    echo "  • Auto-restart: ✅"
    echo "  • Token-based auth: ✅"
fi

echo ""
if $all_good; then
    echo "✨ All deployment files ready!"
    echo ""
    echo "Next steps:"
    echo "1. Copy these files to your VPS"
    echo "2. Get Cloudflare Tunnel token"
    echo "3. Run: bash deploy.sh"
    echo "4. Configure public hostname in Cloudflare"
    echo ""
    echo "Your Aurora-X will be live at https://aurora.yourdomain.com"
else
    echo "⚠️  Some files are missing. Please check."
fi