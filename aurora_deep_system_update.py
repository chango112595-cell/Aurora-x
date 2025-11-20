#!/usr/bin/env python3
"""
Aurora Deep System Update - COMPLETE VERSION
Scans ENTIRE program and updates ALL outdated tier/capability references

Based on successful manual updates from chat history:
- 27 tiers → 53 tiers
- 32 tiers → 53 tiers  
- 41 tiers → 53 tiers
- 46 tiers → 53 tiers
- 54 total/capabilities → 66 total/capabilities
- 1500 skills → 2500 skills
- TIER 28-32 → TIER 28-53
"""

import re
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Set


class AuroraDeepUpdater:
    """Deep search and update across entire codebase"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.updates_made = []
        self.scanned = 0
        
        # Extensions to scan
        self.extensions = {'.py', '.ts', '.tsx', '.js', '.jsx', '.md', '.txt', '.json', '.sh', '.ps1'}
        
        # Dirs to skip
        self.skip_dirs = {'node_modules', '.git', '__pycache__', 'dist', 'build', '.venv', 'venv'}
        
        # Replacement patterns (old_pattern, new_value, description)
        self.patterns = [
            # Tier counts
            (r'\b27 tier', '53 tier', '27 tiers → 53 tiers'),
            (r'\b27 Tier', '53 Tier', '27 Tiers → 53 Tiers'),
            (r'\b27 TIER', '53 TIER', '27 TIERS → 53 TIERS'),
            (r'tier[s]?\s+27', 'tiers 53', 'tiers 27 → tiers 53'),
            
            (r'\b32 tier', '53 tier', '32 tiers → 53 tiers'),
            (r'\b32 Tier', '53 Tier', '32 Tiers → 53 Tiers'),
            (r'\b32 TIER', '53 TIER', '32 TIERS → 53 TIERS'),
            
            (r'\b41 tier', '53 tier', '41 tiers → 53 tiers'),
            (r'\b41 Tier', '53 Tier', '41 Tiers → 53 Tiers'),
            (r'\b41 TIER', '53 TIER', '41 TIERS → 53 TIERS'),
            
            (r'\b46 tier', '53 tier', '46 tiers → 53 tiers'),
            (r'\b46 Tier', '53 Tier', '46 Tiers → 53 Tiers'),
            
            # Total capabilities
            (r'\b54 total', '66 total', '54 total → 66 total'),
            (r'\b54 Total', '66 Total', '54 Total → 66 Total'),
            (r'\b54 capabilit', '66 capabilit', '54 capabilities → 66 capabilities'),
            (r'\b54 Capabilit', '66 Capabilit', '54 Capabilities → 66 Capabilities'),
            (r'\b54 system', '66 system', '54 systems → 66 systems'),
            (r'\b54 System', '66 System', '54 Systems → 66 Systems'),
            
            # Specific phrases
            (r'13 Tasks \+ 41 Tiers', '13 Tasks + 53 Tiers', 'Task + Tier formula'),
            (r'13 tasks \+ 41 tiers', '13 tasks + 53 tiers', 'task + tier formula'),
            (r'\(13 Tasks \+ 41 Tiers\)', '(13 Tasks + 53 Tiers)', 'Task + Tier in parens'),
            
            # Skills count
            (r'\b1500\+ skill', '2500+ skill', '1500+ skills → 2500+ skills'),
            (r'\b1,500\+ skill', '2,500+ skill', '1,500+ skills → 2,500+ skills'),
            
            # Tier ranges
            (r'TIER 28-32', 'TIER 28-53', 'TIER range update'),
            (r'Tier 28-32', 'Tier 28-53', 'Tier range update'),
            (r'tier 28-32', 'tier 28-53', 'tier range update'),
            (r'Tiers 28-32', 'Tiers 28-53', 'Tiers range update'),
            (r'tiers 28-32', 'tiers 28-53', 'tiers range update'),
            
            (r'TIER 36-41', 'TIER 36-53', 'TIER range update'),
            (r'Tiers 36-41', 'Tiers 36-53', 'Tiers range update'),
            
            (r'Tier 1-27', 'Tier 1-53', 'Full tier range'),
            (r'TIER 1-27', 'TIER 1-53', 'Full tier range'),
            
            # Architecture descriptions
            (r'13 foundations \+ 41 tiers', '13 foundations + 53 tiers', 'foundations + tiers'),
            (r'13 Foundations \+ 41 Tiers', '13 Foundations + 53 Tiers', 'Foundations + Tiers'),
            
            # Specific component text
            (r'TIER 32 creativity', 'TIER 53 creativity', 'TIER 32 → TIER 53'),
            (r'TIER 32 Architecture', 'TIER 53 Architecture', 'TIER 32 → TIER 53'),
            (r'TIER 32: Architecture', 'TIER 53: Architecture', 'TIER 32 → TIER 53'),
            
            # "tiers_loaded" in Python
            (r'"tiers_loaded":\s*27', '"tiers_loaded": 53', 'tiers_loaded value'),
            (r'"tiers_loaded":\s*32', '"tiers_loaded": 53', 'tiers_loaded value'),
            (r'"tiers_loaded":\s*41', '"tiers_loaded": 53', 'tiers_loaded value'),
            
            # Verification messages
            (r'\(41 tiers, 54 systems\)', '(53 tiers, 66 systems)', 'verification msg'),
            (r'\(32 tiers, 54 systems\)', '(53 tiers, 66 systems)', 'verification msg'),
            (r'\(27 tiers, 54 systems\)', '(53 tiers, 66 systems)', 'verification msg'),
        ]

    def should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed"""
        # Skip excluded directories
        for parent in file_path.parents:
            if parent.name in self.skip_dirs:
                return False
        
        # Only process files with relevant extensions
        return file_path.suffix in self.extensions

    def scan_and_update_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Scan and update a single file"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            original = content
            changes = []
            
            # Apply all patterns
            for pattern, replacement, description in self.patterns:
                matches = list(re.finditer(pattern, content, re.IGNORECASE))
                if matches:
                    content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                    changes.append(f"{description} ({len(matches)} occurrences)")
            
            # If content changed, write it back
            if content != original:
                file_path.write_text(content, encoding='utf-8')
                return True, changes
            
            return False, []
            
        except Exception as e:
            print(f"  ⚠️  Error processing {file_path}: {e}")
            return False, []

    def scan_directory(self, directory: Path = None) -> None:
        """Recursively scan and update all files"""
        if directory is None:
            directory = self.project_root
        
        for item in directory.iterdir():
            # Skip hidden files/dirs and excluded dirs
            if item.name.startswith('.') and item.name not in {'.github'}:
                continue
            
            if item.is_dir():
                if item.name not in self.skip_dirs:
                    self.scan_directory(item)
            elif item.is_file():
                self.scanned += 1
                if self.should_process_file(item):
                    updated, changes = self.scan_and_update_file(item)
                    if updated:
                        rel_path = item.relative_to(self.project_root)
                        self.updates_made.append((str(rel_path), changes))
                        print(f"  ✅ {rel_path}")
                        for change in changes:
                            print(f"     • {change}")

    def run(self) -> None:
        """Run deep system update"""
        print("\n" + "=" * 80)
        print("🔍 AURORA DEEP SYSTEM UPDATE - SCANNING ENTIRE PROGRAM")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        print("\n🎯 Target Updates:")
        print("  • 27/32/41/46 tiers → 53 tiers")
        print("  • 54 total/capabilities/systems → 66")
        print("  • 1500 skills → 2500 skills")
        print("  • TIER 28-32 → TIER 28-53")
        print("  • TIER 36-41 → TIER 36-53")
        
        print("\n📂 Scanning all files...")
        self.scan_directory()
        
        print("\n" + "=" * 80)
        print("✅ DEEP SYSTEM UPDATE COMPLETE")
        print("=" * 80)
        print(f"\n📊 Statistics:")
        print(f"  • Files scanned: {self.scanned}")
        print(f"  • Files updated: {len(self.updates_made)}")
        
        if self.updates_made:
            print(f"\n📝 Updated Files ({len(self.updates_made)}):")
            for file_path, changes in self.updates_made:
                print(f"\n  {file_path}")
                for change in changes:
                    print(f"    • {change}")
        
        # Save report
        report_file = self.project_root / '.aurora_knowledge' / 'deep_update_report.json'
        report_file.parent.mkdir(exist_ok=True)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'scanned': self.scanned,
            'updated': len(self.updates_made),
            'files': [{'path': p, 'changes': c} for p, c in self.updates_made]
        }
        
        import json
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Report saved: {report_file}")
        print("\n" + "=" * 80)
        print("🚀 AURORA SYSTEM FULLY SYNCHRONIZED")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    updater = AuroraDeepUpdater()
    updater.run()
