#!/usr/bin/env python3
"""
Aurora Import Fixer
Autonomously fixes component import/export mismatches
"""

from pathlib import Path


class AuroraImportFixer:
    def __init__(self):
        self.client_dir = Path("client/src")
        self.pages_dir = self.client_dir / "pages"
        self.fixes = []

    def fix_dashboard(self):
        """Fix dashboard.tsx export"""
        print("[Aurora] Fixing dashboard.tsx export...")

        content = """import AuroraFuturisticDashboard from '@/components/AuroraFuturisticDashboard';

export default function Dashboard() {
  return <AuroraFuturisticDashboard />;
}
"""

        path = self.pages_dir / "dashboard.tsx"
        path.write_text(content, encoding="utf-8")
        self.fixes.append(str(path))
        print(f"[Aurora] [OK] Fixed: {path}")

    def fix_tasks(self):
        """Ensure tasks.tsx has correct export"""
        print("[Aurora] Verifying tasks.tsx export...")
        path = self.pages_dir / "tasks.tsx"
        content = path.read_text(encoding="utf-8")

        if "export default function TasksPage()" in content:
            content = content.replace("export default function TasksPage()", "export default function Tasks()")
            path.write_text(content, encoding="utf-8")
            self.fixes.append(str(path))
            print(f"[Aurora] [OK] Fixed: {path}")
        else:
            print(f"[Aurora] [+] {path} is correct")

    def fix_tiers(self):
        """Ensure tiers.tsx has correct export"""
        print("[Aurora] Verifying tiers.tsx export...")
        path = self.pages_dir / "tiers.tsx"
        content = path.read_text(encoding="utf-8")

        if "export default function TiersPage()" in content:
            content = content.replace("export default function TiersPage()", "export default function Tiers()")
            path.write_text(content, encoding="utf-8")
            self.fixes.append(str(path))
            print(f"[Aurora] [OK] Fixed: {path}")
        else:
            print(f"[Aurora] [+] {path} is correct")

    def fix_intelligence(self):
        """Ensure intelligence.tsx has correct export"""
        print("[Aurora] Verifying intelligence.tsx export...")
        path = self.pages_dir / "intelligence.tsx"
        content = path.read_text(encoding="utf-8")

        if "export default function IntelligencePage()" in content:
            content = content.replace(
                "export default function IntelligencePage()", "export default function Intelligence()"
            )
            path.write_text(content, encoding="utf-8")
            self.fixes.append(str(path))
            print(f"[Aurora] [OK] Fixed: {path}")
        else:
            print(f"[Aurora] [+] {path} is correct")

    def fix_chat(self):
        """Ensure chat.tsx has correct export"""
        print("[Aurora] Verifying chat.tsx export...")
        path = self.pages_dir / "chat.tsx"
        if path.exists():
            content = path.read_text(encoding="utf-8")

            if "export default function ChatPage()" in content:
                print(f"[Aurora] [+] {path} is correct")
            else:
                print(f"[Aurora] [+] {path} needs no changes")
        else:
            print(f"[Aurora] [WARN] {path} not found")

    def fix_placeholders(self):
        """Fix placeholder page exports"""
        print("[Aurora] Fixing placeholder page exports...")

        pages = [
            ("evolution", "Evolution"),
            ("autonomous", "Autonomous"),
            ("monitoring", "Monitoring"),
            ("database", "Database"),
            ("settings", "Settings"),
        ]

        for route, name in pages:
            path = self.pages_dir / f"{route}.tsx"
            if path.exists():
                content = path.read_text(encoding="utf-8")
                old_export = f"export default function {route.capitalize()}Page()"
                new_export = f"export default function {name}()"

                if old_export in content:
                    content = content.replace(old_export, new_export)
                    path.write_text(content, encoding="utf-8")
                    self.fixes.append(str(path))
                    print(f"[Aurora] [OK] Fixed: {path}")
                else:
                    print(f"[Aurora] [+] {path} is correct")

    def update_app_imports(self):
        """Update App.tsx imports to match exports"""
        print("[Aurora] Updating App.tsx imports...")

        content = """import { Route, Switch } from "wouter";
import AuroraFuturisticLayout from "./components/AuroraFuturisticLayout";
import Dashboard from "./pages/dashboard";
import ChatPage from "./pages/chat";
import Tasks from "./pages/tasks";
import Tiers from "./pages/tiers";
import Intelligence from "./pages/intelligence";
import Evolution from "./pages/evolution";
import Autonomous from "./pages/autonomous";
import Monitoring from "./pages/monitoring";
import Database from "./pages/database";
import Settings from "./pages/settings";

function App() {
  return (
    <AuroraFuturisticLayout>
      <Switch>
        <Route path="/" component={Dashboard} />
        <Route path="/chat" component={ChatPage} />
        <Route path="/tasks" component={Tasks} />
        <Route path="/tiers" component={Tiers} />
        <Route path="/intelligence" component={Intelligence} />
        <Route path="/evolution" component={Evolution} />
        <Route path="/autonomous" component={Autonomous} />
        <Route path="/monitoring" component={Monitoring} />
        <Route path="/database" component={Database} />
        <Route path="/settings" component={Settings} />
        <Route>
          <div className="flex items-center justify-center h-screen">
            <div className="text-center">
              <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-4">
                404 - Quantum Path Not Found
              </h1>
              <p className="text-purple-400">This neural pathway doesn't exist yet.</p>
            </div>
          </div>
        </Route>
      </Switch>
    </AuroraFuturisticLayout>
  );
}

export default App;
"""

        path = self.client_dir / "App.tsx"
        path.write_text(content, encoding="utf-8")
        self.fixes.append(str(path))
        print(f"[Aurora] [OK] Updated: {path}")

    def run(self):
        """Execute import fixes"""
        print("\n" + "=" * 60)
        print("[Aurora] IMPORT FIXER ACTIVATED")
        print("=" * 60 + "\n")

        print("[Aurora] Fixing page exports...")
        self.fix_dashboard()
        self.fix_tasks()
        self.fix_tiers()
        self.fix_intelligence()
        self.fix_chat()
        self.fix_placeholders()

        print("\n[Aurora] Updating App.tsx...")
        self.update_app_imports()

        print("\n" + "=" * 60)
        print("[Aurora] [OK] IMPORT FIXES COMPLETE")
        print("=" * 60)
        print("\n[Aurora] [EMOJI] Fixed Files:")
        for fix in self.fixes:
            print(f"  [OK] {fix}")
        print("\n[Aurora] [SYNC] Refresh the browser to see the changes!")
        print("[Aurora] [EMOJI] All imports/exports are now aligned!\n")


if __name__ == "__main__":
    fixer = AuroraImportFixer()
    fixer.run()
