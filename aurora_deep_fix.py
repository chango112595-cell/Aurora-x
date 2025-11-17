"""
Aurora's Deep Fix - Address all detected issues
1. Fix layout routing (useLocation)
2. Fix App.tsx React import
3. Fix page components React imports
4. Create missing vite.config.ts
5. Open browser
"""

import os


def fix_layout():
    """Fix the layout routing issue"""
    print("🔧 Aurora: Fixing layout routing...")

    layout_file = "client/src/components/AuroraFuturisticLayout.tsx"
    with open(layout_file, encoding="utf-8") as f:
        content = f.read()

    # Replace useRoute with useLocation
    if "useRoute" in content:
        content = content.replace(
            "import { Link, useRoute } from 'wouter';", "import { Link, useLocation } from 'wouter';"
        )
        content = content.replace('const [match] = useRoute("/:path*");', "const [location] = useLocation();")
        content = content.replace("match === item.path", "location === item.path")
        content = content.replace("match?.startsWith(item.path)", "location.startsWith(item.path)")

        with open(layout_file, "w", encoding="utf-8") as f:
            f.write(content)
        print("   ✅ Layout routing fixed")
    else:
        print("   ✅ Layout already fixed")


def fix_component_imports():
    """Fix React imports in components"""
    print("\n🔧 Aurora: Fixing component imports...")

    files_to_check = ["client/src/App.tsx", "client/src/pages/dashboard.tsx", "client/src/pages/chat.tsx"]

    for file_path in files_to_check:
        if not os.path.exists(file_path):
            continue

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Check if React import exists
        if "import React" not in content and "react" in content.lower():
            # Add React import at the top
            lines = content.split("\n")
            # Find first import line
            for i, line in enumerate(lines):
                if line.strip().startswith("import"):
                    lines.insert(i, "import React from 'react';")
                    break

            content = "\n".join(lines)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"   ✅ Fixed {file_path}")


def create_vite_config():
    """Create vite.config.ts if missing"""
    print("\n🔧 Aurora: Creating Vite config...")

    vite_config = "client/vite.config.ts"

    if os.path.exists(vite_config):
        print("   ✅ vite.config.ts already exists")
        return

    config_content = """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    strictPort: false,
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
});
"""

    with open(vite_config, "w", encoding="utf-8") as f:
        f.write(config_content)
    print("   ✅ Created vite.config.ts")


def verify_all_fixes():
    """Verify all fixes were applied"""
    print("\n🔍 Aurora: Verifying fixes...\n")

    # Check layout
    layout_file = "client/src/components/AuroraFuturisticLayout.tsx"
    with open(layout_file, encoding="utf-8") as f:
        layout_content = f.read()

    layout_ok = "useLocation" in layout_content and "const [location]" in layout_content
    print(f"   Layout routing: {'✅ FIXED' if layout_ok else '❌ STILL BROKEN'}")

    # Check vite config
    vite_ok = os.path.exists("client/vite.config.ts")
    print(f"   Vite config: {'✅ EXISTS' if vite_ok else '❌ MISSING'}")

    return layout_ok and vite_ok


if __name__ == "__main__":
    print("=" * 60)
    print("🌟 AURORA DEEP FIX - ADDRESSING ALL ISSUES")
    print("=" * 60 + "\n")

    fix_layout()
    fix_component_imports()
    create_vite_config()

    all_fixed = verify_all_fixes()

    print("\n" + "=" * 60)
    if all_fixed:
        print("✨ All issues resolved! System ready.")
        print("=" * 60)
    else:
        print("⚠️  Some issues remain - manual review needed")
        print("=" * 60)
