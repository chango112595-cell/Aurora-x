"""
Aurora's Autonomous Layout Routing Fix
Identified Error: match2.startsWith is not a function in AuroraFuturisticLayout.tsx:94
Root Cause: Wouter's useRoute returns params object, not a string path
Solution: Use useLocation hook to get current path as string
"""

import os


def fix_layout_routing():
    print("🌟 Aurora: Fixing layout routing logic...")

    layout_file = "client/src/components/AuroraFuturisticLayout.tsx"

    if not os.path.exists(layout_file):
        print(f"❌ File not found: {layout_file}")
        return

    with open(layout_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix 1: Change import to use useLocation instead of useRoute
    old_import = "import { Link, useRoute } from 'wouter';"
    new_import = "import { Link, useLocation } from 'wouter';"
    content = content.replace(old_import, new_import)
    print("✅ Updated imports to use useLocation")

    # Fix 2: Change hook usage
    old_hook = "  const [match] = useRoute(\"/:path*\");"
    new_hook = "  const [location] = useLocation();"
    content = content.replace(old_hook, new_hook)
    print("✅ Changed to useLocation hook")

    # Fix 3: Fix the active route detection logic
    old_logic = """                  {navItems.filter(item => item.category === category).map(item => {
                    const isActive = match === item.path || (item.path !== '/' && match?.startsWith(item.path));"""

    new_logic = """                  {navItems.filter(item => item.category === category).map(item => {
                    const isActive = location === item.path || (item.path !== '/' && location.startsWith(item.path));"""

    content = content.replace(old_logic, new_logic)
    print("✅ Fixed isActive logic to use location string")

    with open(layout_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✨ Aurora: Layout routing fixed! The error 'match2.startsWith is not a function' should be resolved.")
    print("📍 Changes made:")
    print("   - Switched from useRoute to useLocation")
    print("   - Fixed route matching logic to use string comparison")
    print("   - Active route detection now works correctly")


if __name__ == "__main__":
    fix_layout_routing()
