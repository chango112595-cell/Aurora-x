#!/bin/bash
# Test ARM compatibility locally

echo "🔍 Testing ARM Compatibility for Aurora-X"
echo "========================================="

# Check current architecture
echo ""
echo "📊 Current System:"
echo "  Architecture: $(uname -m)"
echo "  OS: $(uname -s)"
echo "  Python: $(python3 --version 2>&1)"

# Check if Docker is available
echo ""
echo "🐳 Docker Support:"
if command -v docker &> /dev/null; then
    echo "  ✅ Docker installed: $(docker --version)"
    
    # Check for buildx
    if docker buildx version &> /dev/null; then
        echo "  ✅ Docker buildx available"
        echo "  Platforms: $(docker buildx ls | grep -A 1 default | tail -1)"
    else
        echo "  ⚠️  Docker buildx not available (needed for cross-platform builds)"
    fi
else
    echo "  ❌ Docker not installed"
fi

# Test Python compatibility
echo ""
echo "🐍 Python ARM Compatibility:"
python3 -c "
import platform
import sys
print(f'  Platform: {platform.platform()}')
print(f'  Machine: {platform.machine()}')
print(f'  Processor: {platform.processor()}')
print(f'  Python Build: {platform.python_build()[0]}')
print(f'  ARM Ready: {\"arm\" in platform.machine().lower() or \"aarch\" in platform.machine().lower()}')
"

# Check for PWA requirements
echo ""
echo "📱 PWA Requirements:"
if [ -f "aurora_x/static/manifest.json" ]; then
    echo "  ✅ manifest.json exists"
else
    echo "  ❌ manifest.json missing"
fi

if [ -f "aurora_x/static/sw.js" ]; then
    echo "  ✅ Service Worker (sw.js) exists"
else
    echo "  ❌ Service Worker missing"
fi

# Test server startup (non-blocking)
echo ""
echo "🚀 Quick Server Test:"
timeout 3 python -m aurora_x.serve 2>&1 | head -5 || echo "  Server quick test complete"

echo ""
echo "========================================="
echo "✅ ARM compatibility check complete!"
echo ""
echo "Next steps:"
echo "  1. Deploy with HTTPS for PWA on phones"
echo "  2. Push to GitHub to trigger ARM CI builds"
echo "  3. Test on real ARM devices (M1 Mac, Android, RPi)"