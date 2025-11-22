#!/usr/bin/env python3
"""
AURORA HTML TO TSX CONVERTER
Converts HTML files to modern TSX/React components
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
import shutil


class AuroraHTMLToTSXConverter:
    def __init__(self):
        self.root = Path(".")
        self.analysis_file = self.root / "AURORA_HTML_ANALYSIS.json"
        self.converted = []
        self.failed = []
        self.skipped = []

    def load_analysis(self) -> Dict:
        """Load the HTML analysis report"""
        if not self.analysis_file.exists():
            print("❌ AURORA_HTML_ANALYSIS.json not found!")
            print("   Run aurora_check_html_files.py first")
            return None

        with open(self.analysis_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def convert_html_to_jsx(self, html_content: str) -> str:
        """Convert HTML syntax to JSX syntax"""
        jsx = html_content

        # Replace class with className
        jsx = re.sub(r'\bclass=', 'className=', jsx)

        # Replace for with htmlFor
        jsx = re.sub(r'\bfor=', 'htmlFor=', jsx)

        # Convert style strings to objects
        style_pattern = r'style="([^"]+)"'

        def style_to_object(match):
            style_str = match.group(1)
            style_props = []
            for prop in style_str.split(';'):
                if ':' in prop:
                    key, value = prop.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    # Convert kebab-case to camelCase
                    key_parts = key.split('-')
                    camel_key = key_parts[0] + \
                        ''.join(word.capitalize() for word in key_parts[1:])
                    style_props.append(f"{camel_key}: '{value}'")

            if style_props:
                return f"style={{{{{', '.join(style_props)}}}}}"
            return ""

        jsx = re.sub(style_pattern, style_to_object, jsx)

        # Self-closing tags
        self_closing = ['img', 'br', 'hr', 'input', 'meta', 'link']
        for tag in self_closing:
            jsx = re.sub(rf'<{tag}([^>]*)(?<!/)>', rf'<{tag}\1 />', jsx)

        # Replace onclick with onClick, onchange with onChange, etc.
        jsx = re.sub(r'\bon([a-z]+)=',
                     lambda m: f'on{m.group(1).capitalize()}=', jsx)

        return jsx

    def extract_body_content(self, html_content: str) -> Tuple[str, List[str]]:
        """Extract body content and external scripts/styles"""
        external_deps = []

        # Find external scripts
        script_pattern = r'<script[^>]*src=["\']([^"\']+)["\'][^>]*></script>'
        for match in re.finditer(script_pattern, html_content):
            src = match.group(1)
            if not src.startswith(('http://', 'https://', '//')):
                external_deps.append(f"// TODO: Import script: {src}")

        # Find external stylesheets
        link_pattern = r'<link[^>]*href=["\']([^"\']+\.css)["\'][^>]*>'
        for match in re.finditer(link_pattern, html_content):
            href = match.group(1)
            if not href.startswith(('http://', 'https://', '//')):
                external_deps.append(f"// TODO: Import stylesheet: {href}")

        # Extract body content
        body_match = re.search(
            r'<body[^>]*>(.*)</body>', html_content, re.DOTALL | re.IGNORECASE)
        if body_match:
            content = body_match.group(1).strip()
        else:
            # If no body tag, use everything between html tags or entire content
            html_match = re.search(
                r'<html[^>]*>(.*)</html>', html_content, re.DOTALL | re.IGNORECASE)
            if html_match:
                content = html_match.group(1).strip()
            else:
                content = html_content.strip()

        return content, external_deps

    def create_tsx_component(
        self, component_name: str, html_content: str, purpose: str
    ) -> str:
        """Create a TSX component from HTML content"""

        # Extract content and dependencies
        body_content, external_deps = self.extract_body_content(html_content)

        # Convert to JSX
        jsx_content = self.convert_html_to_jsx(body_content)

        # Create component
        tsx = f"""import React from 'react';

{chr(10).join(external_deps) if external_deps else ''}

interface {component_name}Props {{
  // Add props as needed
}}

/**
 * {component_name}
 * Purpose: {purpose}
 * Converted from HTML to TSX by Aurora
 */
export default function {component_name}(props: {component_name}Props) {{
  return (
    <>
{self.indent_content(jsx_content, 6)}
    </>
  );
}}
"""
        return tsx

    def indent_content(self, content: str, spaces: int) -> str:
        """Indent content by specified number of spaces"""
        indent = ' ' * spaces
        lines = content.split('\n')
        return '\n'.join(indent + line if line.strip() else '' for line in lines)

    def get_component_name(self, file_path: Path) -> str:
        """Generate a component name from file path"""
        name = file_path.stem

        # For files in runs/ folders, include the run timestamp to make unique
        if 'runs' in file_path.parts:
            # Extract run timestamp (e.g., run-20251012-205907)
            for part in file_path.parts:
                if part.startswith('run-'):
                    # Get just the timestamp part
                    timestamp = part.replace('run-', '').replace('-', '')
                    name = f"{name}_{timestamp}"
                    break

        # Convert to PascalCase
        parts = re.split(r'[-_]', name)
        component_name = ''.join(word.capitalize() for word in parts if word)
        # Ensure it starts with a capital letter
        if not component_name or not component_name[0].isupper():
            component_name = 'Aurora' + component_name
        return component_name

    def convert_file(self, html_path: Path, tsx_path: Path, purpose: str) -> bool:
        """Convert a single HTML file to TSX"""
        try:
            # Read HTML
            html_content = html_path.read_text(encoding="utf-8")

            # Get component name (now includes timestamp for runs/)
            component_name = self.get_component_name(html_path)

            # Update tsx_path to use unique component name
            tsx_path = tsx_path.parent / f"{component_name}.tsx"

            # Create TSX
            tsx_content = self.create_tsx_component(
                component_name, html_content, purpose)

            # Create directory if needed
            tsx_path.parent.mkdir(parents=True, exist_ok=True)

            # Write TSX
            tsx_path.write_text(tsx_content, encoding="utf-8")

            return True

        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

    def convert_all(self, analysis: Dict):
        """Convert all HTML files to TSX"""
        files_to_convert = analysis.get("files_to_convert", [])

        if not files_to_convert:
            print("❌ No files to convert found in analysis")
            return

        print(f"\n🚀 AURORA HTML TO TSX CONVERSION")
        print(f"   Converting {len(files_to_convert)} files...\n")

        for file_info in files_to_convert:
            html_file = self.root / file_info["file"]
            tsx_file = self.root / file_info["suggested_tsx"]
            purpose = file_info["purpose"]

            if not html_file.exists():
                print(f"⚠️  SKIP {html_file} (not found)")
                self.skipped.append(str(html_file))
                continue

            print(f"🔄 Converting {html_file.name}...")
            print(f"   → {tsx_file}")

            if self.convert_file(html_file, tsx_file, purpose):
                print(f"   ✅ Converted successfully")
                self.converted.append({
                    "html": str(html_file),
                    "tsx": str(tsx_file),
                    "purpose": purpose
                })
            else:
                print(f"   ❌ Failed to convert")
                self.failed.append(str(html_file))

            print()

    def generate_report(self):
        """Generate conversion report"""
        report = {
            "timestamp": "2025-11-22",
            "total_converted": len(self.converted),
            "total_failed": len(self.failed),
            "total_skipped": len(self.skipped),
            "converted_files": self.converted,
            "failed_files": self.failed,
            "skipped_files": self.skipped,
        }

        report_file = self.root / "AURORA_HTML_TSX_CONVERSION_REPORT.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print("\n" + "=" * 60)
        print("📊 CONVERSION SUMMARY")
        print("=" * 60)
        print(f"✅ Converted: {len(self.converted)}")
        print(f"❌ Failed: {len(self.failed)}")
        print(f"⚠️  Skipped: {len(self.skipped)}")
        print(f"\n💾 Report saved: {report_file}")

        if self.converted:
            print(f"\n🎯 Next Steps:")
            print(f"   1. Review converted TSX files in src/components/")
            print(f"   2. Update imports in your main components")
            print(f"   3. Add proper TypeScript interfaces for props")
            print(f"   4. Test each converted component")
            print(f"   5. Delete old HTML files once verified")

    def run(self):
        """Run the conversion"""
        print("\n🌟 AURORA HTML TO TSX CONVERTER")
        print("=" * 60)

        # Load analysis
        analysis = self.load_analysis()
        if not analysis:
            return

        # Convert files
        self.convert_all(analysis)

        # Generate report
        self.generate_report()

        print("\n✅ CONVERSION COMPLETE!")


if __name__ == "__main__":
    converter = AuroraHTMLToTSXConverter()
    converter.run()
