#!/usr/bin/env python3
"""
Aurora Autonomous Route Fixer
Updates default route to open futuristic dashboard automatically
"""

from pathlib import Path


class AuroraRouteFixer:
    """Aurora fixes her own routing"""

    def __init__(self):
        self.root = Path(".")

    def log(self, message):
        print(f"[Aurora] {message}")

    def fix_default_route(self):
        """Aurora changes default route to dashboard"""
        self.log("🔀 Updating default route to dashboard...")

        app_file = self.root / "client/src/App.tsx"
        if not app_file.exists():
            self.log("❌ App.tsx not found")
            return False

        content = app_file.read_text(encoding="utf-8")

        # Replace the default route from ChatPage to Dashboard
        old_route = '<Route path="/" component={ChatPage} />'
        new_route = '<Route path="/" component={Dashboard} />'

        if old_route in content:
            updated_content = content.replace(old_route, new_route)
            app_file.write_text(updated_content, encoding="utf-8")
            self.log("✅ Changed default route: / → Dashboard")
            self.log("✅ Futuristic dashboard will now open automatically!")
            return True
        else:
            self.log("⚠️  Route already configured or pattern not found")
            return False

    def execute(self):
        """Execute the route fix"""
        self.log("=" * 70)
        self.log("🌌 AURORA AUTONOMOUS ROUTE FIX")
        self.log("=" * 70)
        self.log("")

        success = self.fix_default_route()

        self.log("")
        self.log("=" * 70)
        if SUCCESS:
            self.log("✅ ROUTE FIX COMPLETE")
            self.log("🚀 Dashboard will open automatically on load")
            self.log("📍 Route: / → Dashboard (Futuristic UI)")
        else:
            self.log("ℹ️  No changes needed")
        self.log("=" * 70)


if __name__ == "__main__":
    print("\n🌌 Aurora: Autonomous Route Fixer\n")
    fixer = AuroraRouteFixer()
    fixer.execute()
    print("\n✨ Aurora has fixed her routing!")
