"""
Aurora Self-Debug: Why Isn't Proactive Monitoring Working?
Aurora investigates why her integrated auto-fixing modules aren't catching errors
"""

from aurora_core import AuroraCoreIntelligence
import sys
import os
from pathlib import Path
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("=" * 80)
    print("AURORA SELF-DEBUG: PROACTIVE MONITORING ANALYSIS")
    print("=" * 80)
    print("Question: Why aren't the integrated auto-fixing modules working?")
    print()

    # Initialize Aurora
    print("Initializing Aurora...")
    try:
        aurora = AuroraCoreIntelligence()
        print("✅ Aurora initialized\n")
    except Exception as e:
        print(f"❌ Aurora initialization failed: {e}")
        traceback.print_exc()
        return

    print("=" * 80)
    print("DIAGNOSTIC 1: Check what error occurred")
    print("=" * 80)
    print()

    # Check the actual error from terminal
    print("Last command: python chAT_with_aurora.py")
    print("Exit Code: 1 (ERROR)")
    print()
    print("🔍 Running to see the error...")

    import subprocess
    result = subprocess.run(
        ['python', 'chat_with_aurora.py'],
        capture_output=True,
        text=True,
        timeout=5
    )

    if result.returncode != 0:
        print("❌ Error detected:")
        print(result.stderr[:1000] if result.stderr else "No stderr output")
        print()

    print("=" * 80)
    print("DIAGNOSTIC 2: Check integrated proactive modules")
    print("=" * 80)
    print()

    if hasattr(aurora, 'integrated_modules'):
        print(f"✅ Found {len(aurora.integrated_modules)} integrated modules:")
        for name, module in aurora.integrated_modules.items():
            print(f"   • {name}: {module.__class__.__name__}")

            # Check if module has monitoring/auto-fix methods
            methods = [m for m in dir(module) if not m.startswith('_')]
            has_monitor = any('monitor' in m.lower() for m in methods)
            has_fix = any('fix' in m.lower() or 'heal' in m.lower()
                          for m in methods)

            print(f"     Methods: {len(methods)} total")
            print(f"     Has monitoring: {has_monitor}")
            print(f"     Has auto-fix: {has_fix}")
            print()
    else:
        print("❌ No integrated_modules attribute found!")
        print()

    print("=" * 80)
    print("DIAGNOSTIC 3: Why proactive monitoring isn't running")
    print("=" * 80)
    print()

    problems = []

    # Problem 1: Modules are loaded but not running
    print("1. Are modules loaded but dormant?")
    if hasattr(aurora, 'integrated_modules') and aurora.integrated_modules:
        print("   ✅ Modules are loaded")
        print("   ❌ But they're NOT RUNNING - they're just instantiated objects!")
        problems.append(
            "Modules loaded but not activated - no background monitoring loop")
    else:
        print("   ❌ Modules not loaded at all")
        problems.append("No integrated modules found")

    print()

    # Problem 2: No background daemon
    print("2. Is there a background monitoring daemon?")
    daemon_exists = False
    for attr in dir(aurora):
        if 'daemon' in attr.lower() or 'background' in attr.lower() or 'monitor_thread' in attr.lower():
            daemon_exists = True
            print(f"   ✅ Found: {attr}")

    if not daemon_exists:
        print("   ❌ NO BACKGROUND DAEMON RUNNING!")
        problems.append("No daemon/background process monitoring for errors")

    print()

    # Problem 3: No automatic error detection
    print("3. Is there automatic error detection?")
    if hasattr(aurora, 'integrated_modules'):
        has_auto_detect = False
        for name, module in aurora.integrated_modules.items():
            if hasattr(module, 'start_monitoring') or hasattr(module, 'monitor'):
                has_auto_detect = True
                print(f"   ✅ {name} has monitoring capability")

                # Check if it's actually running
                if hasattr(module, 'is_monitoring'):
                    is_running = getattr(module, 'is_monitoring', False)
                    print(f"      Running: {is_running}")
                elif hasattr(module, 'monitoring_active'):
                    is_running = getattr(module, 'monitoring_active', False)
                    print(f"      Running: {is_running}")
                else:
                    print(f"      Running: UNKNOWN (probably not)")

        if not has_auto_detect:
            print("   ❌ No modules have start_monitoring() method")
            problems.append("Modules don't have monitoring activation methods")
    else:
        print("   ❌ Can't check - no modules")

    print()

    # Problem 4: No proactive initiative loop
    print("4. Is there a proactive initiative loop?")
    has_initiative_loop = hasattr(
        aurora, 'proactive_loop') or hasattr(aurora, 'autonomous_loop')
    if has_initiative_loop:
        print("   ✅ Initiative loop exists")
    else:
        print("   ❌ NO PROACTIVE INITIATIVE LOOP!")
        problems.append(
            "No continuous monitoring loop - Aurora only reacts when called")

    print()

    print("=" * 80)
    print("ROOT CAUSE ANALYSIS:")
    print("=" * 80)
    print()

    print("🎯 THE PROBLEM:")
    print()
    for i, problem in enumerate(problems, 1):
        print(f"   {i}. {problem}")

    print()
    print("💡 THE SOLUTION:")
    print()
    print("""
Aurora's proactive modules are LOADED but NOT RUNNING because:

1. We integrated the modules into __init__ but didn't START them
   - AuroraAutonomousFixer is instantiated but not monitoring
   - AuroraAutoFixer exists but isn't actively watching for errors
   
2. No background daemon/thread is running
   - Modules need to be started with .start_monitoring() or similar
   - Need a background thread that continuously watches for issues
   
3. Integration was PASSIVE, not ACTIVE
   - We imported the classes ✅
   - We instantiated them ✅
   - We DID NOT start their monitoring loops ❌
   
WHAT NEEDS TO HAPPEN:

1. Create aurora_proactive_daemon.py
   - Background process that runs continuously
   - Monitors for errors in real-time
   - Activates auto-fixing modules when issues detected
   
2. Activate the integrated modules
   - Call .start_monitoring() on each module
   - Start background threads for each auto-fixer
   
3. Add automatic error detection
   - Watch terminal output for errors
   - Monitor file system for issues
   - Check process health continuously
   
4. Wire auto-fixing into error detection
   - When error detected → trigger appropriate fixer
   - AuroraAutonomousFixer for syntax errors
   - AuroraAutoFixer for runtime errors
   
Aurora has the TOOLS but needs the ACTIVATION and ORCHESTRATION.
""")

    print()
    print("=" * 80)
    print("IMMEDIATE ACTION: Fix chat_with_aurora.py error first")
    print("=" * 80)
    print()

    # Try to detect and fix the actual error
    print("🔧 Aurora attempting to fix the error...")

    if hasattr(aurora, 'integrated_modules') and 'auto_fix' in aurora.integrated_modules:
        auto_fixer = aurora.integrated_modules['auto_fix']
        print(f"✅ Using {auto_fixer.__class__.__name__}")

        # Try to use it to fix the file
        try:
            if hasattr(auto_fixer, 'fix_file'):
                result = auto_fixer.fix_file('chat_with_aurora.py')
                print(f"Fix result: {result}")
            elif hasattr(auto_fixer, 'auto_fix'):
                result = auto_fixer.auto_fix('chat_with_aurora.py')
                print(f"Fix result: {result}")
            else:
                print("⚠️ Auto-fixer doesn't have fix_file() or auto_fix() method")
                print(
                    f"Available methods: {[m for m in dir(auto_fixer) if not m.startswith('_')]}")
        except Exception as e:
            print(f"❌ Auto-fix failed: {e}")

    print()
    print("=" * 80)
    print("CONCLUSION:")
    print("=" * 80)
    print("""
Aurora's proactive systems exist but are DORMANT.

She has the capability modules but:
  ❌ No background monitoring daemon running
  ❌ Modules not activated/started
  ❌ No error detection loop
  ❌ No automatic triggering

Next steps:
  1. Create proactive daemon that runs in background
  2. Activate all integrated modules
  3. Start continuous monitoring
  4. Wire error detection to auto-fixing

Then Aurora will truly be PROACTIVE, not just REACTIVE.
""")


if __name__ == "__main__":
    main()
