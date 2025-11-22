#!/usr/bin/env python3
"""
AURORA HTML TO TSX CONVERTER
Scan for HTML files and convert them to modern TSX/React components
"""

import os
import json
from pathlib import Path


class AuroraHTMLChecker:
    def __init__(self):
        self.root = Path(__file__).parent
        self.html_files = []
        self.conversions_needed = []

    def scan_for_html(self):
        """Find all HTML files in the project"""
        print("🔍 Scanning for HTML files...")
        print("=" * 70)

        # Skip these directories
        skip_dirs = {'node_modules', 'venv', '.venv', 'dist',
                     'build', '__pycache__', '.git', 'backups'}

        for html_file in self.root.rglob('*.html'):
            # Skip if in excluded directory
            if any(skip_dir in html_file.parts for skip_dir in skip_dirs):
                continue

            rel_path = html_file.relative_to(self.root)
            size = html_file.stat().st_size

            self.html_files.append({
                'path': str(rel_path),
                'full_path': html_file,
                'size': size
            })

            print(f"  📄 {rel_path} ({size} bytes)")

        print(f"\n  Total HTML files found: {len(self.html_files)}")
        return self.html_files

    def analyze_html_files(self):
        """Analyze each HTML file to determine if it needs conversion"""
        print("\n📊 Analyzing HTML files...")
        print("=" * 70)

        for html_info in self.html_files:
            html_path = html_info['full_path']

            try:
                content = html_path.read_text(encoding='utf-8')

                # Determine the purpose
                purpose = 'unknown'
                needs_conversion = True

                if 'aurora' in content.lower() and 'chat' in content.lower():
                    purpose = 'Aurora Chat Interface'
                elif 'test' in html_path.name.lower():
                    purpose = 'Test file'
                    needs_conversion = False  # Keep test files
                elif 'demo' in html_path.name.lower():
                    purpose = 'Demo file'
                elif 'dashboard' in content.lower():
                    purpose = 'Dashboard'
                elif 'template' in html_path.name.lower():
                    purpose = 'Template'
                elif html_path.name == 'index.html':
                    purpose = 'Entry point'
                    needs_conversion = False  # Keep index.html as entry

                conversion_info = {
                    'file': str(html_info['path']),
                    'purpose': purpose,
                    'needs_conversion': needs_conversion,
                    'size': html_info['size']
                }

                if needs_conversion:
                    # Suggest TSX equivalent
                    tsx_name = html_path.stem + '.tsx'
                    suggested_location = self.suggest_tsx_location(
                        purpose, tsx_name)
                    conversion_info['suggested_tsx'] = suggested_location

                self.conversions_needed.append(conversion_info)

                status = "🔄 CONVERT" if needs_conversion else "✅ KEEP"
                print(f"\n  {status} {html_info['path']}")
                print(f"     Purpose: {purpose}")
                if needs_conversion:
                    print(
                        f"     → Suggested TSX: {conversion_info.get('suggested_tsx', 'N/A')}")

            except Exception as e:
                print(f"  ⚠️  Error reading {html_info['path']}: {e}")

        return self.conversions_needed

    def suggest_tsx_location(self, purpose, tsx_name):
        """Suggest where the TSX file should go"""
        purpose_map = {
            'Aurora Chat Interface': f'src/components/{tsx_name}',
            'Dashboard': f'src/components/Dashboard/{tsx_name}',
            'Demo file': f'src/demos/{tsx_name}',
            'Template': f'src/templates/{tsx_name}',
            'unknown': f'src/components/{tsx_name}'
        }

        return purpose_map.get(purpose, f'src/components/{tsx_name}')

    def generate_conversion_plan(self):
        """Generate conversion plan"""
        print("\n" + "=" * 70)
        print("📋 CONVERSION PLAN")
        print("=" * 70)

        files_to_convert = [
            c for c in self.conversions_needed if c['needs_conversion']]
        files_to_keep = [
            c for c in self.conversions_needed if not c['needs_conversion']]

        print(f"\n✅ Files to keep as HTML: {len(files_to_keep)}")
        for file_info in files_to_keep:
            print(f"   • {file_info['file']} - {file_info['purpose']}")

        print(f"\n🔄 Files to convert to TSX: {len(files_to_convert)}")
        for file_info in files_to_convert:
            print(f"   • {file_info['file']}")
            print(f"     → {file_info['suggested_tsx']}")

        if not files_to_convert:
            print("\n✨ No HTML files need conversion!")
            print("   All HTML is either necessary (index.html) or test files")
        else:
            print(f"\n💡 RECOMMENDATION:")
            print(
                f"   Convert {len(files_to_convert)} HTML files to modern TSX components")
            print(f"   This will make the codebase fully TypeScript/React based")

        return files_to_convert

    def save_report(self):
        """Save analysis report"""
        report = {
            'total_html_files': len(self.html_files),
            'files_to_keep': [c for c in self.conversions_needed if not c['needs_conversion']],
            'files_to_convert': [c for c in self.conversions_needed if c['needs_conversion']],
            'all_files': self.conversions_needed
        }

        report_file = self.root / 'AURORA_HTML_ANALYSIS.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        print(f"\n💾 Report saved: {report_file.name}")

    def run_analysis(self):
        """Run complete analysis"""
        print("=" * 70)
        print("🌟 AURORA HTML TO TSX ANALYSIS")
        print("=" * 70)
        print("\nChecking for HTML files that should be TSX...\n")

        self.scan_for_html()
        self.analyze_html_files()
        files_to_convert = self.generate_conversion_plan()
        self.save_report()

        print("\n" + "=" * 70)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 70)

        if files_to_convert:
            print(
                f"\n🎯 Found {len(files_to_convert)} HTML files to convert to TSX")
            print("   Run conversion to modernize the codebase")
        else:
            print("\n✨ Codebase is already using TSX/React!")
            print("   No HTML conversions needed")

        return files_to_convert


if __name__ == '__main__':
    checker = AuroraHTMLChecker()
    files_to_convert = checker.run_analysis()
