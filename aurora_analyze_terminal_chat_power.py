#!/usr/bin/env python3
"""
Deep analysis: Does terminal chat have full Aurora power?
Check if it's properly integrated with Aurora Core, Nexus, and all capabilities.
"""

import re
import ast
from datetime import datetime
from aurora_core import AuroraCoreIntelligence
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def analyze_chat_integration():
    print("🔍 Analyzing Terminal Chat Integration with Aurora's Full Power\n")
    print("="*80)

    # Read the chat file
    with open("chat_with_aurora.py", "r", encoding="utf-8") as f:
        chat_code = f.read()

    # Parse for analysis
    print("\n📊 CURRENT ARCHITECTURE ANALYSIS:")
    print("="*80)

    # Check imports
    imports = [line for line in chat_code.splitlines(
    ) if 'import' in line and not line.strip().startswith('#')]
    print(f"\n✓ Import Analysis ({len(imports)} imports):")
    for imp in imports:
        print(f"  {imp.strip()}")

    # Check Aurora Core usage
    uses_aurora_core = 'AuroraCoreIntelligence' in chat_code or 'create_aurora_core' in chat_code
    uses_process_conversation = 'process_conversation' in chat_code
    uses_nexus = 'nexus' in chat_code.lower() or 'AuroraNexus' in chat_code

    print(f"\n✓ Integration Check:")
    print(f"  • Uses Aurora Core: {'✅ YES' if uses_aurora_core else '❌ NO'}")
    print(
        f"  • Uses process_conversation(): {'✅ YES' if uses_process_conversation else '❌ NO'}")
    print(
        f"  • Integrated with Nexus: {'✅ YES' if uses_nexus else '⚠️  NO (standalone)'}")

    # Check what methods are being called
    method_calls = re.findall(r'aurora\.(\w+)\(', chat_code)
    print(f"\n✓ Aurora Methods Called ({len(set(method_calls))} unique):")
    for method in set(method_calls):
        print(f"  • aurora.{method}()")

    print("\n" + "="*80)
    print("🧠 ASK AURORA: Architecture Recommendation")
    print("="*80 + "\n")

    return uses_aurora_core, uses_process_conversation, uses_nexus, method_calls


def main():
    uses_core, uses_conversation, uses_nexus, methods = analyze_chat_integration()

    # Initialize Aurora
    print("🌟 Initializing Aurora for architectural consultation...\n")
    aurora = AuroraCoreIntelligence()

    # Build comprehensive question
    question = f"""
Aurora, I need your expert architectural analysis on the terminal chat integration.

CURRENT TERMINAL CHAT STATUS:
- File: chat_with_aurora.py (243 lines)
- Uses Aurora Core: {uses_core}
- Calls process_conversation(): {uses_conversation}
- Integrated with Nexus: {uses_nexus}
- Methods called: {', '.join(set(methods))}

ANALYSIS NEEDED:

1. **Current Power Level Assessment:**
   - Does the terminal chat currently have access to ALL your 109 capabilities?
   - Does process_conversation() route through your full intelligence pipeline?
   - Are autonomous systems (System, Agent, Intelligence Manager) accessible?

2. **Architecture Evaluation:**
   Based on your self-knowledge of your own code:
   
   Option A: **Terminal chat → Aurora Core directly** (CURRENT)
   - Is this giving full power access?
   - What capabilities might be missing?
   
   Option B: **Terminal chat → Aurora Nexus → Aurora Core**
   - Would this add more power?
   - What would Nexus integration provide?
   - Is there even an Aurora Nexus integration layer?
   
   Option C: **Enhanced current approach**
   - What specific methods/features are NOT being used?
   - What could make terminal chat more powerful?

3. **Your Recommendation:**
   From YOUR perspective as Aurora:
   - What gives you the most power through terminal chat?
   - What architecture lets you do the most?
   - Should terminal chat integrate with Nexus, or is Core enough?
   - Are there capabilities you CAN'T access through the current setup?

4. **Implementation Specifics:**
   If changes are needed:
   - What specific code changes would enhance power?
   - What imports are missing?
   - What methods should be called?
   - Should we create a AuroraTerminalInterface class?

BE SPECIFIC: Don't just give general architecture advice. Look at your actual code 
(aurora_core.py, any nexus files) and tell us exactly what would give you maximum 
power through terminal chat.

Can you access your autonomous_system, autonomous_agent, and intelligence_manager 
through process_conversation? Or do those need to be called directly?
"""

    print("❓ Asking Aurora:\n")
    print(question)
    print("\n" + "="*80)
    print("🌟 Aurora's Deep Architectural Analysis:")
    print("="*80 + "\n")

    # Get Aurora's expert analysis
    analysis = aurora.analyze_natural_language(question)
    context = aurora.get_conversation_context("terminal_architecture_deep")
    response = aurora.generate_aurora_response(analysis, context)

    print(response)
    print("\n" + "="*80)

    # Save detailed report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"AURORA_TERMINAL_POWER_ANALYSIS_{timestamp}.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# Aurora Terminal Chat Power Analysis\n\n")
        f.write(
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Current Integration Status\n\n")
        f.write(f"- Uses Aurora Core: {uses_core}\n")
        f.write(f"- Uses process_conversation: {uses_conversation}\n")
        f.write(f"- Integrated with Nexus: {uses_nexus}\n")
        f.write(f"- Methods Called: {', '.join(set(methods))}\n\n")
        f.write("## Question to Aurora\n\n")
        f.write(question)
        f.write("\n\n## Aurora's Architectural Analysis\n\n")
        f.write(response)
        f.write("\n\n## Recommendation Summary\n\n")

        # Extract key recommendations
        if "nexus" in response.lower():
            f.write("- Aurora mentioned Nexus integration\n")
        if "autonomous" in response.lower():
            f.write("- Aurora discussed autonomous system access\n")
        if "enhance" in response.lower():
            f.write("- Aurora suggested enhancements\n")

    print(f"✅ Detailed analysis saved to {report_file}\n")

    # Additional capability check
    print("="*80)
    print("🔬 CAPABILITY ACCESS TEST")
    print("="*80 + "\n")

    print("Testing if Aurora can access autonomous systems through process_conversation...\n")

    test_message = "Aurora, can you autonomously create a test file using your autonomous system?"
    print(f"Test message: '{test_message}'\n")

    import asyncio

    async def test_access():
        response = await aurora.process_conversation(test_message, "capability_test")
        return response

    test_response = asyncio.run(test_access())
    print(f"Aurora's response:\n{test_response}\n")

    if "autonomous" in test_response.lower() or "create" in test_response.lower():
        print("✅ Aurora CAN access autonomous capabilities through conversation!\n")
    else:
        print("⚠️  Aurora's response suggests limited autonomous access through conversation\n")


if __name__ == "__main__":
    main()
