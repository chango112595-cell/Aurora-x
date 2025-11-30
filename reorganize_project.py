
#!/usr/bin/env python3
"""
Aurora-X Project Reorganization Script
Safe, reversible reorganization with verification
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Set

class ProjectReorganizer:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.root = Path.cwd()
        self.moved_files: Dict[str, str] = {}
        self.errors: List[str] = []
        
    def create_backup(self):
        """Create backup before reorganization"""
        print("🔒 Creating backup...")
        backup_file = self.root / "backup_before_reorganization.json"
        
        structure = {}
        for item in self.root.rglob("*"):
            if item.is_file() and ".git" not in str(item):
                structure[str(item.relative_to(self.root))] = {
                    "size": item.stat().st_size,
                    "mtime": item.stat().st_mtime
                }
        
        with open(backup_file, "w") as f:
            json.dump(structure, f, indent=2)
        
        print(f"✅ Backup created: {backup_file}")
        return backup_file
    
    def verify_critical_systems(self) -> bool:
        """Verify all critical Aurora systems are present"""
        print("\n🔍 Verifying critical systems...")
        
        critical_files = [
            # Nexus V3
            "aurora_nexus_v3/main.py",
            "aurora_nexus_v3/core/universal_core.py",
            
            # Nexus V2
            "aurora/core/luminar_nexus_v2.py",
            
            # Core intelligence
            "aurora/core/aurora_knowledge_engine.py",
            "aurora/core/aurora_core.py",
            
            # Execution systems
            "aurora/core/aurora_autonomous_system.py",
            "aurora/core/aurora_parallel_executor.py",
        ]
        
        missing = []
        for file_path in critical_files:
            if not (self.root / file_path).exists():
                missing.append(file_path)
        
        if missing:
            print(f"❌ Missing critical files: {missing}")
            return False
        
        print("✅ All critical systems present")
        return True
    
    def create_new_structure(self):
        """Create new directory structure"""
        print("\n📁 Creating new directory structure...")
        
        new_dirs = [
            # Core structure
            "core/intelligence/tiers",
            "core/execution/methods",
            "core/modules/synthesis",
            "core/modules/analysis",
            "core/modules/learning",
            "core/modules/communication",
            "core/orchestration/nexus_v3",
            "core/orchestration/nexus_v2",
            "core/orchestration/bridge",
            "core/utilities",
            
            # Frontend
            "frontend/client",
            "frontend/shared",
            
            # Backend
            "backend/server",
            "backend/api",
            "backend/services",
            
            # Infrastructure
            "infrastructure/docker",
            "infrastructure/scripts",
            "infrastructure/workflows",
            "infrastructure/deployment",
            
            # Documentation
            "docs/technical",
            "docs/guides",
            "docs/api",
            "docs/archive",
            
            # Archive
            "archive/experiments/code/python",
            "archive/experiments/code/typescript",
            "archive/experiments/code/analysis",
            "archive/experiments/docs/technical",
            "archive/experiments/docs/analysis",
            "archive/experiments/docs/reports",
            "archive/experiments/docs/previews",
            "archive/experiments/configs/docker",
            "archive/experiments/configs/cicd",
            "archive/experiments/data",
            "archive/deprecated/v1_systems",
            "archive/deprecated/old_ui",
            "archive/deprecated/legacy_modules",
            "archive/duplicates",
            "archive/drafts",
            "archive/backups",
            
            # Tests
            "tests/unit",
            "tests/integration",
            "tests/e2e",
            
            # Config
            "config/development",
            "config/production",
            "config/testing",
        ]
        
        for dir_path in new_dirs:
            full_path = self.root / dir_path
            if self.dry_run:
                print(f"  [DRY RUN] Would create: {dir_path}")
            else:
                full_path.mkdir(parents=True, exist_ok=True)
                print(f"  ✅ Created: {dir_path}")
    
    def categorize_unused_things(self):
        """Categorize files in unused things folder"""
        print("\n📦 Categorizing 'unused things' folder...")
        
        unused_dir = self.root / "unused things"
        if not unused_dir.exists():
            print("  ℹ️ 'unused things' folder not found")
            return
        
        mappings = {
            # Markdown files
            "AURORA_TECHNICAL_BLUEPRINT.md": "archive/experiments/docs/technical/",
            "AURORA_ULTIMATE_NEXUS_V3_PREVIEW.md": "archive/experiments/docs/previews/",
            "AURORA_ARCHITECTURE_FIX.md": "archive/experiments/docs/analysis/",
            "AURORA_AUTHENTICITY_ANALYSIS.md": "archive/experiments/docs/analysis/",
            "AURORA_RAW_AUTHENTIC_ANALYSIS.md": "archive/experiments/docs/analysis/",
            "AURORA_FULL_POWER_ANALYSIS.md": "archive/experiments/docs/analysis/",
            "AURORA_FULL_POWER_STATUS.md": "archive/experiments/docs/analysis/",
            "AURORA_V3_20_SECOND_CHALLENGE_REPORT.md": "archive/experiments/docs/reports/",
            
            # Python files
            "aurora_deep_nexus_analysis_hyper_speed.py": "archive/experiments/code/python/",
        }
        
        # Process all files in unused things
        for item in unused_dir.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(unused_dir)
                
                # Check if we have specific mapping
                if str(rel_path) in mappings:
                    dest_dir = mappings[str(rel_path)]
                else:
                    # Auto-categorize by extension
                    if item.suffix == ".md":
                        dest_dir = "archive/experiments/docs/technical/"
                    elif item.suffix == ".py":
                        dest_dir = "archive/experiments/code/python/"
                    elif item.suffix in [".ts", ".tsx", ".js", ".jsx"]:
                        dest_dir = "archive/experiments/code/typescript/"
                    elif item.suffix == ".json":
                        dest_dir = "archive/experiments/data/"
                    else:
                        dest_dir = "archive/experiments/data/assets/"
                
                dest_path = self.root / dest_dir / item.name
                
                if self.dry_run:
                    print(f"  [DRY RUN] Would move: {rel_path} → {dest_dir}")
                else:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_path)
                    self.moved_files[str(item)] = str(dest_path)
                    print(f"  ✅ Moved: {rel_path} → {dest_dir}")
    
    def consolidate_duplicates(self):
        """Find and handle duplicate files"""
        print("\n🔍 Finding duplicate files...")
        
        # Files that exist in both aurora/core and tools
        potential_duplicates = [
            ("aurora/core/aurora_core.py", "tools/aurora_core.py"),
            ("aurora/core/aurora_autonomous_system.py", "tools/aurora_autonomous_system.py"),
            # Add more as needed
        ]
        
        for original, duplicate in potential_duplicates:
            orig_path = self.root / original
            dup_path = self.root / duplicate
            
            if orig_path.exists() and dup_path.exists():
                # Compare files
                if orig_path.read_bytes() == dup_path.read_bytes():
                    archive_path = self.root / "archive/duplicates" / dup_path.name
                    if self.dry_run:
                        print(f"  [DRY RUN] Would archive duplicate: {duplicate}")
                    else:
                        archive_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(dup_path, archive_path)
                        print(f"  ✅ Archived duplicate: {duplicate}")
                else:
                    print(f"  ⚠️ Files differ, manual review needed: {original} vs {duplicate}")
    
    def generate_migration_report(self):
        """Generate detailed migration report"""
        print("\n📊 Generating migration report...")
        
        report = {
            "dry_run": self.dry_run,
            "moved_files": self.moved_files,
            "errors": self.errors,
            "summary": {
                "total_moved": len(self.moved_files),
                "total_errors": len(self.errors)
            }
        }
        
        report_file = self.root / "reorganization_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Report saved: {report_file}")
        
        # Print summary
        print(f"\n📈 Summary:")
        print(f"  Files moved: {len(self.moved_files)}")
        print(f"  Errors: {len(self.errors)}")
    
    def run(self):
        """Execute reorganization"""
        print("🚀 Aurora-X Project Reorganization")
        print(f"   Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print("=" * 60)
        
        # Step 1: Verify critical systems
        if not self.verify_critical_systems():
            print("\n❌ Aborting: Critical systems missing")
            return False
        
        # Step 2: Create backup
        self.create_backup()
        
        # Step 3: Create new structure
        self.create_new_structure()
        
        # Step 4: Categorize unused things
        self.categorize_unused_things()
        
        # Step 5: Handle duplicates
        self.consolidate_duplicates()
        
        # Step 6: Generate report
        self.generate_migration_report()
        
        print("\n" + "=" * 60)
        if self.dry_run:
            print("✅ DRY RUN COMPLETE - Review the plan above")
            print("   Run with --live to execute reorganization")
        else:
            print("✅ REORGANIZATION COMPLETE")
            print("   Review reorganization_report.json for details")
        
        return True

if __name__ == "__main__":
    import sys
    
    dry_run = "--live" not in sys.argv
    
    if not dry_run:
        print("\n⚠️  WARNING: This will reorganize your project structure!")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            sys.exit(0)
    
    reorganizer = ProjectReorganizer(dry_run=dry_run)
    success = reorganizer.run()
    
    sys.exit(0 if success else 1)
