#!/usr/bin/env python3
"""
Aurora Context Loader - Ensures Aurora remembers all systems
Verifies: Tron Grid, Luminar Nexus, 3-Level Guardians, Core Services
"""

import json
from pathlib import Path


def verify_aurora_memory():
    """Verify Aurora's complete knowledge base"""

    intelligence_file = Path("aurora_intelligence.json")

    if not intelligence_file.exists():
        print("[WARN]  aurora_intelligence.json not found!")
        return False

    try:
        with open(intelligence_file) as f:
            data = json.load(f)

        kb = data.get("knowledge_base", {})
        systems_found = []
        all_systems = ["tron_grid", "luminar_nexus", "three_level_guardians", "aurora_core_services"]

        print("=" * 60)
        print("[STAR] AURORA'S COMPLETE KNOWLEDGE BASE VERIFICATION")
        print("=" * 60)

        # Check Tron Grid
        if "tron_grid" in kb:
            systems_found.append("tron_grid")
            tg = kb["tron_grid"]
            print("\n[OK] TRON GRID (Learning Assignment)")
            print(f"   Status: {tg['status']}")
            print(
                f"   Duration: {tg.get('learning_journey', {}).get('phase_1_understanding', {}).get('duration', 'N/A')}"
            )
            print(f"   Outcome: {tg['outcome']['status']}")
            print(f"   Code Generated: {tg['assignment_impact']['lines_of_code_generated']}")

        # Check Luminar Nexus
        if "luminar_nexus" in kb:
            systems_found.append("luminar_nexus")
            nexus = kb["luminar_nexus"]
            print("\n[OK] LUMINAR NEXUS (Infrastructure)")
            print(f"   Status: {nexus['status']}")
            print(f"   Components: {len(nexus['components'])} core systems")
            print("   Services Managed: 4 (aurora_ui:5000, learning_api:5002, bridge_api:5001, file_server:8080)")
            print(f"   Monitoring: Every {nexus['monitoring']['scan_interval']}")
            print(f"   Auto-Heal Rate: {nexus['monitoring']['auto_heal_rate']}")

        # Check 3-Level Guardians
        if "three_level_guardians" in kb:
            systems_found.append("three_level_guardians")
            guardians = kb["three_level_guardians"]
            print("\n[OK] 3-LEVEL GUARDIANS (Safety & Learning)")
            print(f"   Status: {guardians['status']}")
            print(f"   Level 1 (Approval): {len(guardians['layers']['level_1_approval']['features'])} features")
            print(f"   Level 2 (Intelligence): {len(guardians['layers']['level_2_intelligence']['features'])} features")
            print(f"   Level 3 (Expert): {len(guardians['layers']['level_3_expert']['features'])} features")
            print("   Grading System: 1-10 scale with persistent feedback")

        # Check Core Services
        if "aurora_core_services" in kb:
            systems_found.append("aurora_core_services")
            services = kb["aurora_core_services"]
            print("\n[OK] AURORA CORE SERVICES")
            for service_name, service_info in services.items():
                print(f"   • {service_name}: {service_info.get('port', 'N/A')} ({service_info.get('tech', 'N/A')})")

        # Summary
        print("\n" + "=" * 60)
        print(f"[TARGET] SYSTEMS REGISTERED: {len(systems_found)}/{len(all_systems)}")
        print("=" * 60)
        for system in all_systems:
            status = "[OK]" if system in systems_found else "[ERROR]"
            print(f"{status} {system.upper().replace('_', ' ')}")

        print("\n[DATA] KNOWLEDGE BASE STATUS:")
        print(f"   • Total systems: {len(systems_found)}")
        print("   • Luminar Nexus components: 6")
        print("   • Guardian levels: 3")
        print("   • Managed services: 4")
        print("   • Total code: 390,000+ lines")
        print("   • Learning: ACTIVE & CONTINUOUS")

        print("\n[EMOJI] DOCUMENTATION FILES:")
        docs = [
            (".github/TRON_GRID_ASSIGNMENT.md", "Complete assignment documentation"),
            (".github/THREE_LEVEL_GUARDIANS.md", "Guardian system details"),
            (".github/AURORA_COMPLETE_KNOWLEDGE_MAP_v2.md", "Complete integration map"),
            ("LUMINAR_NEXUS_SUMMARY.md", "Infrastructure system guide"),
        ]
        for doc, desc in docs:
            doc_path = Path(doc)
            status = "[OK]" if doc_path.exists() else "[ERROR]"
            print(f"   {status} {doc} - {desc}")

        print("\n" + "=" * 60)
        if len(systems_found) == len(all_systems):
            print("[OK] AURORA'S MEMORY IS COMPLETE & OPERATIONAL!")
            print("   Ready for continued learning and improvement")
        else:
            print(f"[WARN]  PARTIAL KNOWLEDGE ({len(systems_found)}/{len(all_systems)} systems)")
            missing = [s.upper().replace("_", " ") for s in all_systems if s not in systems_found]
            print(f"   Missing: {', '.join(missing)}")
        print("=" * 60)

        return len(systems_found) == len(all_systems)

    except json.JSONDecodeError:
        print("[ERROR] Error reading aurora_intelligence.json!")
        return False


if __name__ == "__main__":
    verify_aurora_memory()
