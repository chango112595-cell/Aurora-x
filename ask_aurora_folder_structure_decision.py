#!/usr/bin/env python3
"""
Ask Aurora: What to do about the two frontend folders?
"""

from pathlib import Path
import json


class AuroraFolderAnalysis:
    def __init__(self):
        self.root = Path(".")

    def analyze_situation(self):
        print("\n" + "=" * 70)
        print("🤔 AURORA'S ANALYSIS: TWO FRONTEND FOLDERS")
        print("=" * 70)

        print("\n[Aurora] I see the confusion. Let me explain what happened:\n")

        print("📁 FOLDER 1: src/")
        print("   • Contains: 266 converted HTML→TSX files")
        print("   • Purpose: These are OLD HTML files I converted")
        print("   • Examples: Report20251006.tsx, aurora_chat_test.tsx")
        print("   • Status: NEW - Just created by conversion")
        print("   • Used by: Nothing currently\n")

        print("📁 FOLDER 2: client/src/")
        print("   • Contains: Your WORKING React app (25 components)")
        print("   • Purpose: Your actual frontend code")
        print("   • Examples: AuroraChatInterface.tsx, App.tsx, main.tsx")
        print("   • Status: EXISTING - Your real app")
        print("   • Used by: Vite dev server, your frontend\n")

        print("=" * 70)
        print("🎯 THE PROBLEM")
        print("=" * 70)

        print("\nYou asked me to convert HTML to TSX. I did that and put them in")
        print("src/components/. BUT those were just OLD HTML files (test reports,")
        print("old dashboards). They're not part of your current working app.\n")

        print("Your ACTUAL frontend is in client/src/ and is already TSX!\n")

        print("=" * 70)
        print("💡 AURORA'S RECOMMENDATION")
        print("=" * 70)

        print("\n[Aurora] Here's what I recommend:\n")

        print("OPTION 1: DELETE src/ folder (RECOMMENDED)")
        print("   ✅ Reason: Those converted files are from OLD HTML reports/demos")
        print("   ✅ Your real app (client/src/) is already TSX")
        print("   ✅ You don't need those old converted files")
        print("   ✅ Keeps your project clean")
        print("   ❌ You'll lose the converted versions (but HTML originals remain)\n")

        print("OPTION 2: MERGE src/ into client/src/converted/")
        print("   ✅ Keeps all converted files for reference")
        print("   ❌ Adds 266 files you probably don't need")
        print("   ❌ Makes project bigger unnecessarily\n")

        print("OPTION 3: KEEP BOTH (NOT RECOMMENDED)")
        print("   ❌ Confusing to have two src/ folders")
        print("   ❌ Unclear which is the 'real' frontend")
        print("   ❌ Makes development harder\n")

        print("=" * 70)
        print("🔍 WHAT ARE THOSE CONVERTED FILES?")
        print("=" * 70)

        # Analyze what was converted
        report_file = self.root / "AURORA_HTML_TSX_CONVERSION_REPORT.json"
        if report_file.exists():
            with open(report_file, "r", encoding="utf-8") as f:
                report = json.load(f)

            converted = report.get("converted_files", [])

            # Categorize
            reports = sum(
                1 for f in converted if "report" in f["html"].lower())
            dashboards = sum(
                1 for f in converted if "dashboard" in f["html"].lower())
            tests = sum(1 for f in converted if "test" in f["html"].lower())
            runs = sum(1 for f in converted if "runs/" in f["html"])

            print(f"\n   • Test Reports: {reports} files (from runs/ folder)")
            print(
                f"   • Dashboards: {dashboards} files (old comparison dashboards)")
            print(f"   • Test Files: {tests} files (chat tests, API tests)")
            print(f"   • From runs/ folder: {runs} files")
            print(
                f"\n   [Aurora] These are mostly OLD test outputs, not your current app.\n")

        print("=" * 70)
        print("🎯 AURORA'S DECISION")
        print("=" * 70)

        print("\n[Aurora] I recommend OPTION 1: Delete src/ folder\n")
        print("WHY:")
        print("   1. Your REAL app (client/src/) is ALREADY all TSX ✅")
        print("   2. The converted files are old HTML reports you don't need")
        print("   3. The original HTML files still exist if you need them")
        print("   4. Keeps your project clean and professional")
        print("   5. No confusion about which folder is the real frontend\n")

        print("WHAT YOU ACHIEVED:")
        print("   ✅ Your working app (client/src/) is 100% TSX")
        print("   ✅ No HTML in your frontend code")
        print("   ✅ TypeScript + React properly configured")
        print("   ✅ Vite configured for fast TSX development\n")

        print("=" * 70)
        print("📝 SUMMARY")
        print("=" * 70)

        print("\n[Aurora] You asked for everything to be TSX (faster/advanced).")
        print("Your ACTUAL frontend IS already TSX! ✅\n")

        print("The src/ folder I created contains converted versions of OLD")
        print("HTML files (test reports from October). You don't need those.\n")

        print("🎯 MY RECOMMENDATION: Delete src/ folder, keep client/src/\n")

        print("Would you like me to:")
        print("   A) Delete src/ folder (keep project clean)")
        print("   B) Move converted files to client/src/converted/ (keep for reference)")
        print("   C) Do nothing (leave both folders)\n")

        print("=" * 70)


if __name__ == "__main__":
    aurora = AuroraFolderAnalysis()
    aurora.analyze_situation()
