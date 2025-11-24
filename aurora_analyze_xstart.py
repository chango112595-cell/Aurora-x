#!/usr/bin/env python3
"""
Aurora: Analyze x-start and determine what you need to activate EVERYTHING
Use 100% power - all 79 capabilities, all grandmaster skills
"""

import asyncio
from aurora_core import create_aurora_core
from pathlib import Path
import os

os.environ["AURORA_CHAT_MODE"] = "true"
os.environ["AURORA_NO_ORCHESTRATION"] = "true"


async def aurora_analyze_xstart():
    print("\n" + "="*80)
    print("[POWER] AURORA 100% POWER ANALYSIS - x-start System")
    print("="*80 + "\n")

    aurora = create_aurora_core()

    # Read x-start file
    xstart_path = Path("x-start")
    if not xstart_path.exists():
        print("[ERROR] x-start file not found!")
        return

    with open(xstart_path, 'r', encoding='utf-8') as f:
        xstart_code = f.read()

    request = f"""Aurora, this is your MOST CRITICAL ANALYSIS. Use EVERY capability:

**YOUR MISSION:**
Analyze the x-start system and tell us EXACTLY what you need to activate EVERYTHING at 100% power.

**USE ALL 188 CAPABILITIES:**
- 66 Knowledge Tiers (all domains)
- 109 Autonomous Modules (all systems)
- Grandmaster Decision-Making
- Autonomous Analysis
- System Architecture Mastery
- ALL your skills

**HERE IS x-start CODE:**
```python
{xstart_code}
```

**WHAT WE NEED TO KNOW:**

1. **What does x-start do?** (complete breakdown)
2. **What services does it start?** (every single one)
3. **What's MISSING?** (services/systems not being started)
4. **What do YOU need to be at 100% power?** (what's not in x-start that should be)
5. **What should be ADDED to x-start?** (complete list)
6. **Architecture issues?** (what's wrong with the current setup)
7. **Dependencies?** (what needs to run first, what needs what)
8. **Your grandmaster recommendation** (how should x-start work for MAXIMUM power)

**BE COMPLETELY TECHNICAL:**
- Analyze EVERY import
- Check EVERY service definition
- Identify EVERY port
- Find EVERY capability module
- List EVERY missing piece

**THEN PROVIDE:**
- The COMPLETE x-start code that activates ALL 79 capabilities
- The EXACT command to run it
- The FULL list of services/systems it should manage

This is about getting Aurora to 100% OPERATIONAL power. Hold nothing back.
Use your grandmaster autonomous decision-making. Be DECISIVE, COMPREHENSIVE, and ACTION-ORIENTED.

ANALYZE NOW."""

    print("REQUEST TO AURORA (100% POWER):")
    print("-" * 80)
    print("Analyzing x-start system with all 79 capabilities...")
    print("-" * 80 + "\n")

    print("AURORA'S GRANDMASTER ANALYSIS:")
    print("="*80 + "\n")

    # Bypass process_conversation - use direct intelligence
    analysis = aurora.analyze_natural_language(request)

    # Use process_conversation for complete analysis
    response = await aurora.process_conversation(
        request,
        session_id="xstart_100_percent_analysis"
    )

    print(response)
    print("\n" + "="*80)

    # Save analysis
    with open("AURORA_XSTART_ANALYSIS.md", "w", encoding="utf-8") as f:
        f.write("# Aurora's 100% Power Analysis - x-start System\n\n")
        f.write("## Current x-start Code\n\n")
        f.write("```python\n")
        f.write(xstart_code)
        f.write("\n```\n\n")
        f.write("## Aurora's Grandmaster Analysis\n\n")
        f.write(response)
        f.write("\n")

    print(f"\n[EMOJI] Saved to: AURORA_XSTART_ANALYSIS.md")

    # Also analyze what files x-start should be managing
    print("\n" + "="*80)
    print("[DATA] SCANNING PROJECT FOR ALL AURORA SYSTEMS...")
    print("="*80 + "\n")

    # Find all Aurora services/systems
    project_root = Path(".")
    services = []

    # Find all Python files that look like services
    for pattern in ["*_server.py", "*_service.py", "*aurora*.py", "*manager*.py"]:
        for file in project_root.glob(pattern):
            if file.name not in ["aurora_conscious.py", "aurora_authentic.py"]:
                services.append(str(file))

    print(f"Found {len(services)} potential service files:\n")
    for service in sorted(services):
        print(f"  • {service}")

    print(f"\n[IDEA] Aurora should analyze if ALL of these should be in x-start\n")

if __name__ == "__main__":
    asyncio.run(aurora_analyze_xstart())
