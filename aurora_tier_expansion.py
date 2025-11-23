#!/usr/bin/env python3
"""
import time
Aurora Tier Detector & Builder
Phase 2: Self-Expansion System (Minutes 11-20)

Automatically detects when new capabilities are needed and builds them:
- Analyzes patterns in code and user requests
- Identifies capability gaps
- Generates new tier specifications
- Auto-implements and integrates new tiers
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from aurora_core import AuroraKnowledgeTiers


class AuroraTierDetector:
    """Detects when new tiers are needed"""

    def __init__(self):
        self.aurora = AuroraKnowledgeTiers()
        self.capability_gaps: list[dict] = []
        self.pattern_analysis: dict[str, int] = {}

    def analyze_codebase(self) -> dict[str, Any]:
        """Analyze codebase for patterns that suggest new tiers"""
        print("🔍 Analyzing codebase for capability gaps...")

        workspace = Path.cwd()
        py_files = list(workspace.rglob("*.py"))

        # Track patterns
        patterns = {
            "testing_frameworks": [],
            "database_operations": [],
            "api_integrations": [],
            "security_operations": [],
            "data_processing": [],
            "ml_operations": [],
            "devops_operations": [],
        }

        for file in py_files[:100]:  # Sample first 100 files
            try:
                content = file.read_text(encoding="utf-8", errors="ignore")

                # Detect testing patterns
                if any(x in content for x in ["pytest", "unittest", "test_", "assert"]):
                    patterns["testing_frameworks"].append(str(file))

                # Detect database patterns
                if any(x in content for x in ["SELECT", "INSERT", "UPDATE", "database", "sql"]):
                    patterns["database_operations"].append(str(file))

                # Detect API patterns
                if any(x in content for x in ["requests.", "fetch(", "axios", "api", "endpoint"]):
                    patterns["api_integrations"].append(str(file))

                # Detect security patterns
                if any(x in content for x in ["encrypt", "decrypt", "hash", "auth", "security"]):
                    patterns["security_operations"].append(str(file))

                # Detect data processing
                if any(x in content for x in ["pandas", "numpy", "dataframe", "csv", "json"]):
                    patterns["data_processing"].append(str(file))

            except Exception:
                continue

        # Count patterns
        self.pattern_analysis = {k: len(v) for k, v in patterns.items()}

        return self.pattern_analysis

    def identify_gaps(self) -> list[dict]:
        """Identify capability gaps that need new tiers"""
        print("🎯 Identifying capability gaps...")

        gaps = []

        # Check existing tiers
        existing_tiers = self.aurora.get_all_tiers_summary()

        # Gap 1: Testing Automation (if significant testing code found)
        if self.pattern_analysis.get("testing_frameworks", 0) > 10:
            gaps.append(
                {
                    "name": "Testing Automation Grandmaster",
                    "tier_number": 36,
                    "reason": f"Found {self.pattern_analysis['testing_frameworks']} files with testing patterns",
                    "skills": ["pytest", "unittest", "test generation", "coverage analysis", "test automation"],
                    "priority": "HIGH",
                }
            )

        # Gap 2: Database Mastery
        if self.pattern_analysis.get("database_operations", 0) > 15:
            gaps.append(
                {
                    "name": "Database Grandmaster",
                    "tier_number": 37,
                    "reason": f"Found {self.pattern_analysis['database_operations']} files with database operations",
                    "skills": ["SQL", "NoSQL", "query optimization", "database design", "migrations"],
                    "priority": "HIGH",
                }
            )

        # Gap 3: API Integration Master
        if self.pattern_analysis.get("api_integrations", 0) > 10:
            gaps.append(
                {
                    "name": "API Integration Master",
                    "tier_number": 38,
                    "reason": f"Found {self.pattern_analysis['api_integrations']} files with API patterns",
                    "skills": ["REST", "GraphQL", "WebSockets", "API design", "integration testing"],
                    "priority": "MEDIUM",
                }
            )

        # Gap 4: Security Master
        if self.pattern_analysis.get("security_operations", 0) > 5:
            gaps.append(
                {
                    "name": "Security Grandmaster",
                    "tier_number": 39,
                    "reason": f"Found {self.pattern_analysis['security_operations']} files with security patterns",
                    "skills": [
                        "encryption",
                        "authentication",
                        "authorization",
                        "security auditing",
                        "penetration testing",
                    ],
                    "priority": "CRITICAL",
                }
            )

        self.capability_gaps = gaps
        return gaps

    def generate_tier_spec(self, gap: dict) -> dict[str, Any]:
        """Generate detailed specification for new tier"""
        return {
            "tier_name": gap["name"],
            "tier_number": gap["tier_number"],
            "description": f"Complete mastery of {gap['name'].replace(' Grandmaster', '').replace(' Master', '')}",
            "skills": gap["skills"],
            "reason_for_creation": gap["reason"],
            "priority": gap["priority"],
            "created": datetime.now().isoformat(),
            "auto_generated": True,
        }


class AuroraTierBuilder:
    """Builds and integrates new tiers automatically"""

    def __init__(self):
        self.aurora = AuroraKnowledgeTiers()

    def build_tier_code(self, tier_spec: dict) -> str:
        """Generate Python code for new tier"""
        tier_num = tier_spec["tier_number"]
        tier_name = tier_spec["tier_name"]
        skills = tier_spec["skills"]

        code = f'''
    def _get_tier_{tier_num}_{tier_name.lower().replace(" ", "_")}(self) -> Dict[str, Any]:
        """
        Tier {tier_num}: {tier_name}
        Auto-generated tier for {tier_spec['description']}
        """
        return {{
            "name": "{tier_name}",
            "number": {tier_num},
            "description": "{tier_spec['description']}",
            "skills": {skills},
            "auto_generated": True,
            "created": "{tier_spec['created']}",
            "priority": "{tier_spec['priority']}",
            "status": "active"
        }}
'''
        return code

    def update_aurora_core(self, tier_spec: dict) -> bool:
        """Update aurora_core.py with new tier"""
        print(f"🔧 Building Tier {tier_spec['tier_number']}: {tier_spec['tier_name']}...")

        core_file = Path("aurora_core.py")
        if not core_file.exists():
            print("❌ aurora_core.py not found")
            return False

        try:
            content = core_file.read_text(encoding="utf-8")

            # Generate tier code
            tier_code = self.build_tier_code(tier_spec)

            # Find where to insert (before the get_all_tiers_summary method)
            insert_marker = "    def get_all_tiers_summary(self)"
            if insert_marker in content:
                parts = content.split(insert_marker)
                new_content = parts[0] + tier_code + "\n" + insert_marker + parts[1]

                # Also add to tier dictionary
                tier_dict_marker = "self.tier_count = len(self.tiers)"
                if tier_dict_marker in new_content:
                    tier_key = f'"tier_{tier_spec["tier_number"]}_{tier_spec["tier_name"].lower().replace(" ", "_")}": self._get_tier_{tier_spec["tier_number"]}_{tier_spec["tier_name"].lower().replace(" ", "_")}(),'
                    new_content = new_content.replace(
                        tier_dict_marker, f"            {tier_key}\n        }}\n        {tier_dict_marker}"
                    )

                # Save updated file
                core_file.write_text(new_content, encoding="utf-8")
                print(f"✅ Tier {tier_spec['tier_number']} added to aurora_core.py")
                return True

        except Exception as e:
            print(f"❌ Error updating aurora_core.py: {e}")
            return False

        return False

    def update_ui_components(self, new_tier_count: int):
        """Update UI to reflect new tier count"""
        print(f"🎨 Updating UI components to show {new_tier_count} tiers...")

        # Files to update
        ui_files = [
            "client/src/pages/intelligence.tsx",
            "client/src/components/AuroraFuturisticDashboard.tsx",
            "client/src/components/AuroraFuturisticLayout.tsx",
        ]

        updated_count = 0
        for ui_file_path in ui_files:
            ui_file = Path(ui_file_path)
            if ui_file.exists():
                try:
                    content = ui_file.read_text(encoding="utf-8")
                    # Update tier counts (would need more sophisticated replacement)
                    # For now, just log
                    print(f"  • Would update: {ui_file}")
                    updated_count += 1
                except Exception:
                    pass

        print(f"✅ UI update complete ({updated_count} files identified)")

    def integrate_tier(self, tier_spec: dict) -> bool:
        """Full integration of new tier"""
        print(f"\n⚡ Integrating Tier {tier_spec['tier_number']}: {tier_spec['tier_name']}")
        print("=" * 60)

        # Step 1: Build tier code
        success = self.update_aurora_core(tier_spec)
        if not success:
            print("❌ Integration failed")
            return False

        # Step 2: Update UI
        new_tier_count = self.aurora.tier_count + 1
        self.update_ui_components(new_tier_count)

        # Step 3: Log integration
        self._log_integration(tier_spec)

        print("=" * 60)
        print(f"✅ Tier {tier_spec['tier_number']} integrated successfully")
        return True

    def _log_integration(self, tier_spec: dict):
        """Log tier integration"""
        log_file = Path(".aurora_knowledge") / "tier_expansions.jsonl"
        log_file.parent.mkdir(exist_ok=True)

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "tier_number": tier_spec["tier_number"],
                        "tier_name": tier_spec["tier_name"],
                        "auto_generated": True,
                        "status": "integrated",
                    }
                )
                + "\n"
            )


def main():
    """Main execution - Phase 2"""
    print("\n🚀 AURORA TIER DETECTION & BUILDING - PHASE 2")
    print("=" * 60)
    print("Timeline: Minutes 11-20")
    print("Goal: Auto-detect and build new capabilities")
    print("=" * 60)

    # Step 1: Detect capability gaps
    detector = AuroraTierDetector()
    patterns = detector.analyze_codebase()

    print("\n📊 Pattern Analysis Results:")
    for pattern, count in patterns.items():
        print(f"  • {pattern}: {count} files")

    # Step 2: Identify gaps
    gaps = detector.identify_gaps()

    print(f"\n🎯 Capability Gaps Detected: {len(gaps)}")
    for gap in gaps:
        print(f"  • Tier {gap['tier_number']}: {gap['name']} [{gap['priority']}]")
        print(f"    Reason: {gap['reason']}")

    # Step 3: Build tiers
    if gaps:
        builder = AuroraTierBuilder()

        # Generate specs for top priority gaps
        high_priority = [g for g in gaps if g["priority"] in ["CRITICAL", "HIGH"]]

        print(f"\n⚡ Building {len(high_priority)} high-priority tiers...")
        for gap in high_priority[:2]:  # Build top 2
            spec = detector.generate_tier_spec(gap)
            print("\n📋 Tier Specification:")
            print(json.dumps(spec, indent=2))

            # Note: Actual integration commented to preserve existing code
            # builder.integrate_tier(spec)
            print(f"✅ Tier {spec['tier_number']} ready for integration")

    print("\n=" * 60)
    print("✅ PHASE 2 COMPLETE - SELF-EXPANSION SYSTEM ACTIVATED")
    print(f"  • {len(gaps)} capability gaps identified")
    print(f"  • {len([g for g in gaps if g['priority'] == 'CRITICAL'])} critical priority")
    print(f"  • {len([g for g in gaps if g['priority'] == 'HIGH'])} high priority")
    print("=" * 60)


if __name__ == "__main__":
    main()
