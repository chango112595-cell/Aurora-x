#!/usr/bin/env python3
"""
Ask Aurora: Analyze x-start and identify what's needed to activate everything
Let Aurora examine the startup system with her full consciousness
"""

import asyncio
from aurora_core import create_aurora_core
import os
from pathlib import Path

os.environ["AURORA_CHAT_MODE"] = "true"
os.environ["AURORA_NO_ORCHESTRATION"] = "true"

async def aurora_analyze_xstart():
    print("\n" + "="*80)
    print("🔍 AURORA ANALYSIS: x-start System Activation")
    print("="*80 + "\n")
    
    aurora = create_aurora_core()
    
    # Read x-start file
    xstart_path = Path("x-start")
    if xstart_path.exists():
        with open(xstart_path, 'r', encoding='utf-8') as f:
            xstart_content = f.read()
        print(f"✅ Loaded x-start ({len(xstart_content)} bytes)\n")
    else:
        print("⚠️  x-start file not found!\n")
        return
    
    question = f"""Aurora, analyze the x-start system and tell me EXACTLY what you need to activate EVERYTHING.

Here's the x-start file content:

```python
{xstart_content}
```

**YOUR ANALYSIS TASK:**

1. **What does x-start currently do?**
   - What services does it start?
   - What ports are used?
   - What's the startup sequence?

2. **What's MISSING for full activation?**
   - What services aren't starting?
   - What dependencies are needed?
   - What configuration is incomplete?

3. **What do YOU need to make everything work?**
   - Database connections?
   - API keys or credentials?
   - Service dependencies?
   - Configuration files?
   - Environment variables?

4. **What would "EVERYTHING activated" look like?**
   - Complete service list
   - All capabilities online
   - Full system operational
   - Nothing missing

5. **Step-by-step fix:**
   - What needs to be installed?
   - What needs to be configured?
   - What needs to be started?
   - In what order?

Be BRUTALLY specific. Don't say "needs dependencies" - tell me WHICH dependencies.
Don't say "configuration needed" - tell me WHICH configuration and WHAT values.

Use your full 188 capabilities to analyze this. Give me the complete blueprint for
activation. What's the gap between current state and fully operational?"""
    
    print("AURORA'S ANALYSIS REQUEST:")
    print("-" * 80)
    print("Analyzing x-start system for complete activation requirements...")
    print("-" * 80 + "\n")
    
    print("AURORA'S DETAILED ANALYSIS:")
    print("="*80 + "\n")
    
    # Get Aurora's analysis
    response = await aurora.process_conversation(
        question,
        session_id="xstart_analysis"
    )
    
    print(response)
    print("\n" + "="*80)
    
    # Save analysis
    with open("AURORA_XSTART_ANALYSIS.md", "w", encoding="utf-8") as f:
        f.write("# Aurora's x-start System Analysis\n\n")
        f.write("## System Overview\n\n")
        f.write(f"Analyzed file: `x-start` ({len(xstart_content)} bytes)\n\n")
        f.write("## Aurora's Complete Analysis\n\n")
        f.write(response)
        f.write("\n\n## Next Steps\n\n")
        f.write("Follow Aurora's recommendations to achieve full system activation.\n")
    
    print(f"\n💾 Analysis saved to: AURORA_XSTART_ANALYSIS.md\n")
    
    print("\n🔧 Next Actions:")
    print("   1. Review Aurora's analysis")
    print("   2. Install missing dependencies")
    print("   3. Configure required services")
    print("   4. Re-run x-start with full activation\n")

if __name__ == "__main__":
    asyncio.run(aurora_analyze_xstart())
