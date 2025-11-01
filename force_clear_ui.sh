#!/bin/bash
# Aurora's Force Clear & Restart Script
# Clears all caches and restarts the UI with fresh state

echo "🌟 Aurora: Force clearing all caches and restarting UI..."
echo "=" 

# Kill current dev server
echo "1️⃣ Stopping current UI server..."
pkill -f "vite" || true
pkill -f "npm run dev" || true
sleep 2

# Clear service worker cache in browser (user needs to do this manually)
echo ""
echo "2️⃣ Service worker has been disabled in code"
echo "   ⚠️  YOU MUST DO THIS MANUALLY:"
echo "   - Open browser Developer Tools (F12)"
echo "   - Go to Application tab"
echo "   - Click 'Service Workers'"
echo "   - Click 'Unregister' next to any workers"
echo "   - Click 'Clear storage' → 'Clear site data'"
echo ""

# Clear node modules cache
echo "3️⃣ Clearing build caches..."
cd /workspaces/Aurora-x
rm -rf client/.vite 2>/dev/null || true
rm -rf client/dist 2>/dev/null || true
rm -rf dist 2>/dev/null || true
rm -rf .vite 2>/dev/null || true

# Clear TypeScript cache
echo "4️⃣ Clearing TypeScript cache..."
rm -rf client/node_modules/.vite 2>/dev/null || true

echo ""
echo "5️⃣ Starting fresh UI server..."
cd /workspaces/Aurora-x/client

# Start dev server
npm run dev &

echo ""
echo "=" 
echo "✅ Aurora: Fresh start initiated!"
echo ""
echo "Next steps:"
echo "1. Wait 5-10 seconds for server to start"
echo "2. Open browser Developer Tools (F12)"
echo "3. Go to Application → Service Workers → Unregister all"
echo "4. Go to Application → Storage → Clear site data"
echo "5. Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)"
echo "6. Go to http://localhost:5000/chat"
echo ""
echo "🌟 Aurora says: The service worker was caching the old UI!"
echo "   After clearing it, you'll see the new Aurora chat interface!"
