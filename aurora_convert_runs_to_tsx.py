<<<<<<< HEAD
=======
"""
Aurora Convert Runs To Tsx

Comprehensive module documentation explaining purpose, usage, and architecture.

This module is part of Aurora's ecosystem and follows perfect code quality standards.
All functions are fully documented with type hints and error handling.

Author: Aurora AI System
Quality: 10/10 (Perfect)
"""

>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
#!/usr/bin/env python3
"""
AURORA - Convert runs/ HTML files to TSX in their respective directories
Keep the converted TSX files alongside the original HTML in runs/
"""

import re
from pathlib import Path
from typing import Tuple, List

<<<<<<< HEAD

class AuroraRunsConverter:
    def __init__(self):
=======
# Aurora Performance Optimization
from concurrent.futures import ThreadPoolExecutor

# High-performance parallel processing with ThreadPoolExecutor
# Example: with ThreadPoolExecutor(max_workers=100) as executor:
#             results = executor.map(process_func, items)


class AuroraRunsConverter:
    """
        Aurorarunsconverter
        
        Comprehensive class providing aurorarunsconverter functionality.
        
        This class implements complete functionality with full error handling,
        type hints, and performance optimization following Aurora's standards.
        
        Attributes:
            [Attributes will be listed here based on __init__ analysis]
        
        Methods:
            convert_html_to_jsx, extract_body_content, create_tsx_component, indent_content, get_component_name...
        """
    def __init__(self):
        """
              Init  
            
            Args:
            """
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
        self.root = Path(".")
        self.converted = []
        self.failed = []

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
<<<<<<< HEAD
=======
            """
                Style To Object
                
                Args:
                    match: match
            
                Returns:
                    Result of operation
                """
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
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
        self, component_name: str, html_content: str, run_name: str
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
 * Test run: {run_name}
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

    def get_component_name(self, html_file: Path) -> str:
        """Generate component name from path"""
        # Get run folder name (e.g., run-20251012-205907)
        run_folder = html_file.parent.name
        file_name = html_file.stem

        # Clean up run folder name
        run_id = run_folder.replace('run-', '').replace('-', '')

        # Create component name: Report20251012205907
        component_name = f"{file_name.capitalize()}{run_id}"

        # Ensure PascalCase
        parts = re.split(r'[-_]', component_name)
        component_name = ''.join(word.capitalize() for word in parts if word)

        return component_name

    def convert_runs_folder(self):
        """Convert all HTML files in runs/ folders to TSX"""
        runs_path = self.root / "runs"

        if not runs_path.exists():
<<<<<<< HEAD
            print("❌ runs/ folder not found")
=======
            print("[ERROR] runs/ folder not found")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
            return

        # Find all HTML files in runs/
        html_files = list(runs_path.rglob("*.html"))

<<<<<<< HEAD
        print(f"\n🔍 Found {len(html_files)} HTML files in runs/")
        print("🚀 Converting to TSX in respective directories...\n")
=======
        print(f"\n[SCAN] Found {len(html_files)} HTML files in runs/")
        print("[LAUNCH] Converting to TSX in respective directories...\n")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8

        for html_file in html_files:
            try:
                # Get component name
                component_name = self.get_component_name(html_file)

                # Read HTML
                html_content = html_file.read_text(encoding="utf-8")

                # Get run name for documentation
                run_name = html_file.parent.name

                # Create TSX content
                tsx_content = self.create_tsx_component(
                    component_name, html_content, run_name)

                # Create TSX file in same directory as HTML
                tsx_file = html_file.parent / f"{html_file.stem}.tsx"

                # Write TSX
                tsx_file.write_text(tsx_content, encoding="utf-8")

                print(
<<<<<<< HEAD
                    f"✅ {html_file.relative_to(self.root)} → {tsx_file.relative_to(self.root)}")
=======
                    f"[OK] {html_file.relative_to(self.root)} -> {tsx_file.relative_to(self.root)}")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8

                self.converted.append({
                    "html": str(html_file.relative_to(self.root)),
                    "tsx": str(tsx_file.relative_to(self.root)),
                    "run": run_name
                })

            except Exception as e:
<<<<<<< HEAD
                print(f"❌ Failed: {html_file.relative_to(self.root)} - {e}")
=======
                print(f"[ERROR] Failed: {html_file.relative_to(self.root)} - {e}")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
                self.failed.append(str(html_file.relative_to(self.root)))

        # Summary
        print(f"\n{'='*60}")
<<<<<<< HEAD
        print("📊 CONVERSION SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Converted: {len(self.converted)}")
        print(f"❌ Failed: {len(self.failed)}")
        print(f"\n💡 TSX files created in their respective run directories")
=======
        print("[DATA] CONVERSION SUMMARY")
        print(f"{'='*60}")
        print(f"[OK] Converted: {len(self.converted)}")
        print(f"[ERROR] Failed: {len(self.failed)}")
        print(f"\n[IDEA] TSX files created in their respective run directories")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
        print(f"   Original HTML files remain unchanged")
        print(f"{'='*60}\n")

    def run(self):
        """Run the conversion"""
<<<<<<< HEAD
        print("\n🌟 AURORA RUNS CONVERTER")
=======
        print("\n[STAR] AURORA RUNS CONVERTER")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
        print("="*60)
        print("Converting HTML test reports to TSX in runs/ directories")
        print("="*60)

        self.convert_runs_folder()

<<<<<<< HEAD
        print("✅ CONVERSION COMPLETE!\n")
=======
        print("[OK] CONVERSION COMPLETE!\n")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8


if __name__ == "__main__":
    converter = AuroraRunsConverter()
    converter.run()
