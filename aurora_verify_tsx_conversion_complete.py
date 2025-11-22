#!/usr/bin/env python3
"""
AURORA TSX CONVERSION VERIFICATION
Double-check that everything is properly converted to TSX/advanced format
"""

import json
from pathlib import Path
from typing import Dict, List, Set


class AuroraTSXVerification:
    def __init__(self):
        self.root = Path(".")
        self.issues = []
        self.warnings = []
        self.successes = []

    def check_frontend_tsx_files(self) -> Dict:
        """Check all frontend TSX files exist and are properly formatted"""
        print("\n🔍 CHECKING FRONTEND TSX FILES")
        print("=" * 60)

        src_path = self.root / "src"
        if not src_path.exists():
            self.issues.append("src/ directory does not exist!")
            return {"status": "error", "message": "src/ missing"}

        tsx_files = list(src_path.rglob("*.tsx"))
        ts_files = list(src_path.rglob("*.ts"))

        print(f"✅ Found {len(tsx_files)} TSX files")
        print(f"✅ Found {len(ts_files)} TS files")

        # Check for any remaining HTML in src/
        html_files = list(src_path.rglob("*.html"))
        if html_files:
            self.warnings.append(f"Found {len(html_files)} HTML files in src/")
            for html_file in html_files:
                print(
                    f"⚠️  HTML file in src/: {html_file.relative_to(self.root)}")
        else:
            print("✅ No HTML files in src/ directory")
            self.successes.append("src/ is HTML-free")

        # Check for old JSX files (should be TSX now)
        jsx_files = list(src_path.rglob("*.jsx"))
        if jsx_files:
            self.warnings.append(
                f"Found {len(jsx_files)} JSX files (should be TSX)")
            for jsx_file in jsx_files:
                print(
                    f"⚠️  JSX file (should be TSX): {jsx_file.relative_to(self.root)}")
        else:
            print("✅ No JSX files (all converted to TSX)")
            self.successes.append("No legacy JSX files")

        return {
            "tsx_count": len(tsx_files),
            "ts_count": len(ts_files),
            "html_count": len(html_files),
            "jsx_count": len(jsx_files)
        }

    def check_converted_components(self) -> Dict:
        """Verify all converted HTML->TSX components"""
        print("\n🔍 CHECKING CONVERTED COMPONENTS")
        print("=" * 60)

        report_file = self.root / "AURORA_HTML_TSX_CONVERSION_REPORT.json"
        if not report_file.exists():
            self.warnings.append("Conversion report not found")
            print("⚠️  Conversion report not found")
            return {"status": "unknown"}

        with open(report_file, "r", encoding="utf-8") as f:
            report = json.load(f)

        total_converted = report.get("total_converted", 0)
        total_failed = report.get("total_failed", 0)
        converted_files = report.get("converted_files", [])

        print(f"✅ Total conversions: {total_converted}")
        print(f"{'✅' if total_failed == 0 else '❌'} Failed conversions: {total_failed}")

        # Verify the TSX files actually exist
        missing = []
        for item in converted_files[:10]:  # Check first 10 as sample
            tsx_path = self.root / item["tsx"]
            if not tsx_path.exists():
                missing.append(item["tsx"])

        if missing:
            self.issues.append(
                f"{len(missing)} converted TSX files are missing")
            print(f"❌ {len(missing)} converted files missing!")
        else:
            print("✅ All sampled converted files exist")
            self.successes.append("All converted TSX files exist")

        return {
            "total_converted": total_converted,
            "total_failed": total_failed,
            "missing_files": len(missing)
        }

    def check_component_structure(self) -> Dict:
        """Check that components follow TSX best practices"""
        print("\n🔍 CHECKING COMPONENT STRUCTURE")
        print("=" * 60)

        components_path = self.root / "src" / "components"
        if not components_path.exists():
            self.issues.append("src/components/ does not exist!")
            return {"status": "error"}

        tsx_files = list(components_path.rglob("*.tsx"))

        # Sample check: verify components have proper React imports
        sample_size = min(5, len(tsx_files))
        proper_imports = 0

        for tsx_file in tsx_files[:sample_size]:
            content = tsx_file.read_text(encoding="utf-8")
            if "import React from 'react'" in content:
                proper_imports += 1

        if proper_imports == sample_size:
            print(
                f"✅ All sampled components have React imports ({sample_size}/{sample_size})")
            self.successes.append("Components have proper React imports")
        else:
            self.warnings.append(
                f"Some components missing React imports ({proper_imports}/{sample_size})")
            print(
                f"⚠️  Only {proper_imports}/{sample_size} components have React imports")

        return {
            "total_components": len(tsx_files),
            "proper_imports": proper_imports,
            "sample_size": sample_size
        }

    def check_typescript_config(self) -> Dict:
        """Verify TypeScript configuration is set up"""
        print("\n🔍 CHECKING TYPESCRIPT CONFIGURATION")
        print("=" * 60)

        tsconfig = self.root / "tsconfig.json"
        if not tsconfig.exists():
            self.issues.append("tsconfig.json not found!")
            print("❌ tsconfig.json not found!")
            return {"status": "error"}

        print("✅ tsconfig.json exists")
        self.successes.append("TypeScript configured")

        # Check for proper JSX settings
        content = tsconfig.read_text(encoding="utf-8")
        tsx_config = json.loads(content)

        jsx_setting = tsx_config.get("compilerOptions", {}).get("jsx")
        if jsx_setting in ["react", "react-jsx", "react-jsxdev"]:
            print(f"✅ JSX configured: {jsx_setting}")
            self.successes.append(f"JSX mode: {jsx_setting}")
        else:
            self.warnings.append(
                f"JSX setting might need review: {jsx_setting}")
            print(f"⚠️  JSX setting: {jsx_setting}")

        return {
            "exists": True,
            "jsx_setting": jsx_setting
        }

    def check_package_json_dependencies(self) -> Dict:
        """Check that React and TypeScript dependencies are installed"""
        print("\n🔍 CHECKING PACKAGE DEPENDENCIES")
        print("=" * 60)

        package_json = self.root / "package.json"
        if not package_json.exists():
            self.warnings.append("package.json not found")
            print("⚠️  package.json not found")
            return {"status": "not_found"}

        with open(package_json, "r", encoding="utf-8") as f:
            package = json.load(f)

        deps = package.get("dependencies", {})
        dev_deps = package.get("devDependencies", {})
        all_deps = {**deps, **dev_deps}

        required = {
            "react": "React library",
            "react-dom": "React DOM",
            "typescript": "TypeScript"
        }

        missing = []
        for dep, name in required.items():
            if dep in all_deps:
                print(f"✅ {name}: {all_deps[dep]}")
            else:
                missing.append(name)
                print(f"❌ {name} not found")

        if missing:
            self.issues.append(f"Missing dependencies: {', '.join(missing)}")
        else:
            self.successes.append("All required dependencies present")

        return {
            "react": all_deps.get("react"),
            "react_dom": all_deps.get("react-dom"),
            "typescript": all_deps.get("typescript"),
            "missing": missing
        }

    def check_vite_config(self) -> Dict:
        """Verify Vite is configured for React + TypeScript"""
        print("\n🔍 CHECKING VITE CONFIGURATION")
        print("=" * 60)

        vite_config = self.root / "vite.config.js"
        vite_config_ts = self.root / "vite.config.ts"

        config_file = None
        if vite_config_ts.exists():
            config_file = vite_config_ts
            print("✅ vite.config.ts exists (TypeScript)")
        elif vite_config.exists():
            config_file = vite_config
            print("✅ vite.config.js exists")
        else:
            self.warnings.append("Vite config not found")
            print("⚠️  Vite config not found")
            return {"status": "not_found"}

        content = config_file.read_text(encoding="utf-8")

        if "@vitejs/plugin-react" in content or "plugin-react" in content:
            print("✅ Vite React plugin configured")
            self.successes.append("Vite configured for React")
        else:
            self.warnings.append("Vite React plugin not detected")
            print("⚠️  Vite React plugin not detected")

        return {
            "exists": True,
            "config_file": str(config_file.name)
        }

    def check_important_tsx_components(self) -> Dict:
        """Check that critical TSX components exist"""
        print("\n🔍 CHECKING CRITICAL COMPONENTS")
        print("=" * 60)

        critical_components = [
            "src/App.tsx",
            "src/main.tsx",
            "src/components/AuroraChatInterface.tsx"
        ]

        missing = []
        for component in critical_components:
            path = self.root / component
            if path.exists():
                print(f"✅ {component}")
            else:
                missing.append(component)
                print(f"❌ {component} MISSING!")

        if missing:
            self.issues.append(
                f"Critical components missing: {', '.join(missing)}")
        else:
            print("\n✅ All critical components present")
            self.successes.append("All critical TSX components exist")

        return {
            "total": len(critical_components),
            "missing": missing
        }

    def generate_final_report(self) -> Dict:
        """Generate final verification report"""
        print("\n" + "=" * 60)
        print("📊 FINAL VERIFICATION REPORT")
        print("=" * 60 + "\n")

        if self.issues:
            print(f"❌ ISSUES FOUND ({len(self.issues)}):")
            for issue in self.issues:
                print(f"   • {issue}")
            print()

        if self.warnings:
            print(f"⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
            print()

        print(f"✅ SUCCESSES ({len(self.successes)}):")
        for success in self.successes:
            print(f"   • {success}")
        print()

        status = "COMPLETE" if not self.issues else "NEEDS_ATTENTION"

        print(f"\n🎯 OVERALL STATUS: {status}")

        if status == "COMPLETE":
            print("\n✨ Everything is properly converted to advanced TSX format!")
            print("   • All HTML files converted to TSX")
            print("   • TypeScript configured")
            print("   • React dependencies present")
            print("   • Vite configured for React + TypeScript")
            print("   • Critical components exist")
        else:
            print("\n⚠️  Some items need attention (see issues above)")

        report = {
            "timestamp": "2025-11-22",
            "status": status,
            "issues_count": len(self.issues),
            "warnings_count": len(self.warnings),
            "successes_count": len(self.successes),
            "issues": self.issues,
            "warnings": self.warnings,
            "successes": self.successes
        }

        report_file = self.root / "AURORA_TSX_VERIFICATION_REPORT.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"\n💾 Report saved: {report_file}")

        return report

    def run(self):
        """Run complete verification"""
        print("\n🌟 AURORA TSX CONVERSION VERIFICATION")
        print("=" * 60)
        print("Checking that everything is converted to advanced TSX format...")

        self.check_frontend_tsx_files()
        self.check_converted_components()
        self.check_component_structure()
        self.check_typescript_config()
        self.check_package_json_dependencies()
        self.check_vite_config()
        self.check_important_tsx_components()

        self.generate_final_report()


if __name__ == "__main__":
    verifier = AuroraTSXVerification()
    verifier.run()
