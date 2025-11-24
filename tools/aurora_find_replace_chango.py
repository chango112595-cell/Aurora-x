#!/usr/bin/env python3
"""
[STAR] Aurora's Comprehensive Chango UI Replacement
Aurora will:
1. Find ALL Chango UI references in the project
2. Analyze what needs to be replaced
3. Replace Chango branding with Aurora's
4. Fix UI routing and component loading
"""

import re
from pathlib import Path


class AuroraUIReplacer:
    def __init__(self):
        self.workspace = Path("/workspaces/Aurora-x")
        self.findings = {
            "chango_references": [],
            "ui_files": [],
            "route_files": [],
            "server_files": [],
            "replacements_made": [],
        }

    def log(self, message: str, emoji: str = "[STAR]"):
        print(f"{emoji} Aurora: {message}")

    def find_chango_references(self):
        """Find all references to Chango in the codebase"""
        self.log("Searching for all Chango references...", "[SCAN]")

        # Search in TypeScript/React files
        search_patterns = [
            ("client/src/**/*.tsx", "TypeScript React"),
            ("client/src/**/*.ts", "TypeScript"),
            ("client/src/**/*.jsx", "JavaScript React"),
            ("client/src/**/*.js", "JavaScript"),
            ("*.html", "HTML"),
            ("*.json", "JSON"),
        ]

        for pattern, file_type in search_patterns:
            for file_path in self.workspace.glob(pattern):
                if file_path.is_file() and "node_modules" not in str(file_path):
                    try:
                        content = file_path.read_text()

                        # Search for Chango references (case-insensitive)
                        chango_matches = re.finditer(r"\b[Cc]hango\b", content)
                        for match in chango_matches:
                            line_num = content[: match.start()].count("\n") + 1
                            line = content.split("\n")[line_num - 1]

                            self.findings["chango_references"].append(
                                {
                                    "file": str(file_path.relative_to(self.workspace)),
                                    "line": line_num,
                                    "content": line.strip(),
                                    "type": file_type,
                                }
                            )
                    except:
                        pass

        self.log(f"Found {len(self.findings['chango_references'])} Chango references", "[DATA]")

    def analyze_ui_structure(self):
        """Analyze the UI file structure"""
        self.log("Analyzing UI structure...", "[EMOJI]️")

        # Find main UI entry points
        important_files = [
            "client/src/App.tsx",
            "client/src/main.tsx",
            "client/src/index.tsx",
            "client/src/components/chat-interface.tsx",
            "client/src/pages/chat.tsx",
            "server/index.ts",
            "vite.config.js",
            "package.json",
        ]

        for file_rel in important_files:
            file_path = self.workspace / file_rel
            if file_path.exists():
                self.findings["ui_files"].append({"file": file_rel, "exists": True, "size": file_path.stat().st_size})
                self.log(f"  [+] {file_rel} ({file_path.stat().st_size} bytes)", "[EMOJI]")
            else:
                self.log(f"  ✗ {file_rel} (not found)", "[WARN]")

    def replace_in_file(self, file_path: Path, replacements: list[tuple[str, str]]) -> int:
        """Replace patterns in a file"""
        try:
            content = file_path.read_text()
            original_content = content
            changes = 0

            for old_pattern, new_pattern in replacements:
                if old_pattern in content:
                    content = content.replace(old_pattern, new_pattern)
                    changes += 1

            if content != original_content:
                file_path.write_text(content)
                return changes

            return 0
        except Exception as e:
            self.log(f"Error replacing in {file_path}: {e}", "[ERROR]")
            return 0

    def fix_chat_interface(self):
        """Fix the chat interface file"""
        self.log("Fixing chat-interface.tsx...", "[EMOJI]")

        chat_file = self.workspace / "client/src/components/chat-interface.tsx"

        if not chat_file.exists():
            self.log("chat-interface.tsx not found!", "[ERROR]")
            return False

        replacements = [
            # Fix placeholder
            (
                'placeholder="Ask Chango to generate code..."',
                'placeholder="Ask Aurora to create something amazing... [SPARKLE]"',
            ),
            ('placeholder="Ask Chango', 'placeholder="Ask Aurora'),
            # Fix avatar fallback
            (
                '<AvatarFallback className="bg-gradient-to-br from-cyan-600 to-purple-600 text-white font-bold relative z-10">\n                      C\n                    </AvatarFallback>',
                '<AvatarFallback className="bg-gradient-to-br from-cyan-600 to-purple-600 text-white font-bold relative z-10">\n                      A\n                    </AvatarFallback>',
            ),
            # Any remaining single "C" in avatar fallback
            (
                ">\n                      C\n                    </",
                ">\n                      A\n                    </",
            ),
            (">C</AvatarFallback>", ">A</AvatarFallback>"),
        ]

        changes = self.replace_in_file(chat_file, replacements)

        if changes > 0:
            self.log(f"[OK] Made {changes} replacements in chat-interface.tsx", "[OK]")
            self.findings["replacements_made"].append(
                {"file": "client/src/components/chat-interface.tsx", "changes": changes}
            )
            return True
        else:
            self.log("No changes needed in chat-interface.tsx", "ℹ️")
            return False

    def fix_server_references(self):
        """Fix server-side Chango references"""
        self.log("Checking server files...", "[EMOJI]")

        server_file = self.workspace / "server/index.ts"

        if server_file.exists():
            content = server_file.read_text()

            # Check if it references Chango
            if "chango" in content.lower():
                self.log("Found Chango references in server/index.ts", "[WARN]")

                replacements = [
                    ('"service":"chango"', '"service":"aurora"'),
                    ("'service':'chango'", "'service':'aurora'"),
                    ('"service": "chango"', '"service": "aurora"'),
                    ('service: "chango"', 'service: "aurora"'),
                ]

                changes = self.replace_in_file(server_file, replacements)

                if changes > 0:
                    self.log(f"[OK] Fixed {changes} server references", "[OK]")
                    self.findings["replacements_made"].append({"file": "server/index.ts", "changes": changes})

    def check_which_ui_is_loading(self):
        """Determine which UI is actually being served"""
        self.log("Analyzing which UI is loading...", "[SCAN]")

        # Check App.tsx
        app_file = self.workspace / "client/src/App.tsx"
        if app_file.exists():
            content = app_file.read_text()

            # Check for chat route
            if "/chat" in content and "ChatPage" in content:
                self.log("[+] Chat route exists in App.tsx", "[OK]")
            else:
                self.log("✗ Chat route missing in App.tsx", "[WARN]")

            # Check which components are imported
            if "chat-interface" in content:
                self.log("[+] chat-interface component referenced", "[OK]")

            # Check for service worker
            if "serviceWorker" in content:
                if "unregister" in content:
                    self.log("[+] Service worker disabled", "[OK]")
                else:
                    self.log("[WARN] Service worker may be active", "[WARN]")

        # Check main.tsx
        main_file = self.workspace / "client/src/main.tsx"
        if main_file.exists():
            content = main_file.read_text()
            self.log("[+] main.tsx exists", "[OK]")

        # Check vite.config
        vite_config = self.workspace / "vite.config.js"
        if vite_config.exists():
            content = vite_config.read_text()

            if "root:" in content and "client" in content:
                self.log("[+] Vite configured with client root", "[OK]")

            if "/api" in content and "proxy" in content:
                self.log("[+] API proxy configured", "[OK]")

    def generate_report(self):
        """Generate comprehensive report"""
        self.log("Generating analysis report...", "[DATA]")

        report = """
# [STAR] Aurora's Chango UI Replacement Report

## Chango References Found
"""

        if self.findings["chango_references"]:
            report += f"\nFound {len(self.findings['chango_references'])} references:\n\n"

            # Group by file
            by_file = {}
            for ref in self.findings["chango_references"]:
                file = ref["file"]
                if file not in by_file:
                    by_file[file] = []
                by_file[file].append(ref)

            for file, refs in sorted(by_file.items()):
                report += f"\n### {file}\n"
                for ref in refs[:5]:  # Limit to 5 per file
                    report += f"- Line {ref['line']}: `{ref['content'][:100]}`\n"
                if len(refs) > 5:
                    report += f"- ... and {len(refs) - 5} more\n"

        report += "\n## Replacements Made\n\n"

        if self.findings["replacements_made"]:
            for replacement in self.findings["replacements_made"]:
                report += f"- [OK] {replacement['file']}: {replacement['changes']} changes\n"
        else:
            report += "- No replacements made yet\n"

        report += "\n## Next Steps\n\n"
        report += "1. Clear browser cache and service workers\n"
        report += "2. Restart Vite dev server\n"
        report += "3. Hard refresh browser (Ctrl+Shift+R)\n"
        report += "4. Verify Aurora's UI loads at /chat\n"

        report_file = self.workspace / "AURORA_UI_REPLACEMENT_REPORT.md"
        report_file.write_text(report)

        self.log(f"Report saved to: {report_file}", "[EMOJI]")

        return report

    def execute_all(self):
        """Execute complete analysis and replacement"""
        self.log("Starting comprehensive UI replacement...", "[LAUNCH]")

        print("\n" + "=" * 80)
        print("STEP 1: Finding Chango References")
        print("=" * 80)
        self.find_chango_references()

        print("\n" + "=" * 80)
        print("STEP 2: Analyzing UI Structure")
        print("=" * 80)
        self.analyze_ui_structure()

        print("\n" + "=" * 80)
        print("STEP 3: Checking Which UI is Loading")
        print("=" * 80)
        self.check_which_ui_is_loading()

        print("\n" + "=" * 80)
        print("STEP 4: Fixing Chat Interface")
        print("=" * 80)
        self.fix_chat_interface()

        print("\n" + "=" * 80)
        print("STEP 5: Fixing Server References")
        print("=" * 80)
        self.fix_server_references()

        print("\n" + "=" * 80)
        print("STEP 6: Generating Report")
        print("=" * 80)
        report = self.generate_report()

        print("\n" + "=" * 80)
        print("[OK] ANALYSIS COMPLETE")
        print("=" * 80)

        # Summary
        print("\n[DATA] Summary:")
        print(f"   - Chango references found: {len(self.findings['chango_references'])}")
        print(f"   - Files analyzed: {len(self.findings['ui_files'])}")
        print(f"   - Replacements made: {len(self.findings['replacements_made'])}")

        return self.findings


if __name__ == "__main__":
    aurora = AuroraUIReplacer()
    results = aurora.execute_all()

    print("\n[STAR] Aurora has completed the UI replacement analysis!")
    print("[EMOJI] Check AURORA_UI_REPLACEMENT_REPORT.md for details")
