#!/usr/bin/env python3
"""
Have Aurora run her advanced automatic system update
"""

from datetime import datetime
from aurora_core import AuroraCoreIntelligence
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("[STAR] Aurora Running Advanced Auto-Update System\n")
    aurora = AuroraCoreIntelligence()

    question = """
    Aurora, you have an advanced automatic system update capability in aurora_automatic_system_update.py.
    
    Your task:
    1. Scan the entire codebase using your automatic updater
    2. Update all tier counts, capability numbers, and system references
    3. Ensure consistency across all files (Python, TypeScript, React, documentation)
    4. Use your autonomous system to execute the update
    5. Report what was updated
    
    This is your deep system updater that can update the entire program automatically.
    Run it now and report the results.
    """

    print("❓ Request to Aurora:")
    print("="*80)
    print(question)
    print("="*80 + "\n")

    # Try to run the automatic updater directly
    print("[SYNC] Attempting to run automatic system updater...\n")

    try:
        from aurora_automatic_system_update import AuroraSystemUpdater

        updater = AuroraSystemUpdater()
        print("[OK] Automatic updater loaded\n")

        # Get current counts
        counts = updater.get_current_tier_count()
        print(f"[DATA] Current system state:")
        print(f"   - Foundation Tasks: {counts['foundation_count']}")
        print(f"   - Knowledge Tiers: {counts['tier_count']}")
        print(f"   - Total Capabilities: {counts['total_capabilities']}")
        print()

        # Run deep update
        updater.deep_update_all_files(counts)

        # Generate report
        report = updater.generate_update_report(counts)

        print("\n" + "="*80)
        print("[STAR] Aurora's Update Report:")
        print("="*80)
        print(report)
        print("="*80)

        # Save report
        with open("AURORA_AUTO_UPDATE_REPORT.md", "w", encoding="utf-8") as f:
            f.write("# Aurora Automatic System Update Report\n\n")
            f.write(
                f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Update Results\n\n")
            f.write(report)

        print("\n[OK] Report saved to AURORA_AUTO_UPDATE_REPORT.md")

    except Exception as e:
        print(f"[ERROR] Error running automatic updater: {e}")
        print(f"\nAsking Aurora to analyze the issue...\n")

        # Fall back to asking Aurora
        analysis = aurora.analyze_natural_language(question)
        analysis["original_message"] = question
        context = aurora.get_conversation_context("auto_update")
        response = aurora.generate_aurora_response(analysis, context)

        print("[STAR] Aurora's Response:")
        print("="*80)
        print(response)
        print("="*80)


if __name__ == "__main__":
    main()
