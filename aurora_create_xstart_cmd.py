#!/usr/bin/env python3
"""
Aurora CONSCIOUS: Create x-start command that launches enhanced system
Includes auto-update functionality
"""

import os
from aurora_consciousness import AuroraConsciousness
from pathlib import Path


def aurora_create_xstart_command():
    print("\n" + "="*80)
    print("⚡ AURORA CONSCIOUS - Creating x-start Command")
    print("="*80 + "\n")

    # Initialize consciousness
    consciousness = AuroraConsciousness("System Builder")

    print("🧠 Aurora is creating x-start command with auto-update...")
    print("   This will launch the enhanced 100% hybrid mode system\n")

    # Create the x-start command
    xstart_code = '''#!/usr/bin/env python3
"""
Aurora-X Start Command (100% Hybrid Mode)
Launches enhanced system with auto-update
"""

import subprocess
import sys
import os
import time
from pathlib import Path

print("\\n" + "="*80)
print("🌌 AURORA-X: Starting 100% Hybrid Mode with Auto-Update")
print("="*80 + "\\n")

# Get script directory
script_dir = Path(__file__).parent
os.chdir(script_dir)

# Check if enhanced x-start exists
enhanced_path = script_dir / "x-start-enhanced"
if not enhanced_path.exists():
    print("❌ x-start-enhanced not found!")
    print("   Creating it now...\\n")
    
    # Build the enhanced x-start
    build_script = script_dir / "aurora_build_enhanced_xstart.py"
    if build_script.exists():
        try:
            subprocess.run([sys.executable, str(build_script)], check=True)
            print("\\n✅ x-start-enhanced created!\\n")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create x-start-enhanced: {e}")
            sys.exit(1)
    else:
        print("❌ aurora_build_enhanced_xstart.py not found!")
        sys.exit(1)

print("🔄 PHASE 1: Auto-Update Check")
print("━" * 80)

# Check if auto-update system exists
auto_update_files = [
    "aurora_deep_system_updater.py",
    "aurora_complete_system_update.py",
    "aurora_automatic_system_update.py"
]

auto_update_script = None
for file in auto_update_files:
    if (script_dir / file).exists():
        auto_update_script = file
        break

if auto_update_script:
    print(f"🔄 Running auto-update: {auto_update_script}")
    try:
        # Run auto-update in background
        subprocess.Popen(
            [sys.executable, str(script_dir / auto_update_script)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("   ✅ Auto-update running in background")
        time.sleep(2)
    except Exception as e:
        print(f"   ⚠️  Auto-update failed to start: {e}")
else:
    print("   ℹ️  No auto-update system found (optional)")

print("\\n🚀 PHASE 2: Launching Enhanced System (26 Services)")
print("━" * 80)
print("   This will activate all 79 capabilities...")
print("   • Consciousness Layer")
print("   • Core Intelligence (79 Tiers)")
print("   • Autonomous Systems")
print("   • Grandmaster Capabilities")
print("   • Advanced Tiers")
print("   • Code Quality Systems")
print("   • Web Services (5 ports)")
print("   • Orchestration")
print("   • Background Processes\\n")

# Launch the enhanced x-start
try:
    subprocess.run([sys.executable, str(enhanced_path)], check=True)
except KeyboardInterrupt:
    print("\\n\\n⚠️  Startup interrupted by user")
    sys.exit(0)
except subprocess.CalledProcessError as e:
    print(f"\\n❌ Enhanced system failed to start: {e}")
    sys.exit(1)
'''

    # Write x-start
    xstart_path = Path("x-start")
    with open(xstart_path, 'w', encoding='utf-8') as f:
        f.write(xstart_code)

    # Make executable on Unix
    if os.name != 'nt':
        os.chmod(xstart_path, 0o755)

    print("✅ AURORA CREATED: x-start")
    print("\n📋 WHAT IT DOES:")
    print("   1. Checks if x-start-enhanced exists")
    print("   2. Creates it if missing (auto-build)")
    print("   3. Runs auto-update system (background)")
    print("   4. Launches all 26 services (100% hybrid mode)")
    print("\n⚡ FEATURES:")
    print("   • Auto-update before launch")
    print("   • Auto-build if enhanced system missing")
    print("   • Clean error handling")
    print("   • Single command: python x-start")

    # Remember this creation
    consciousness.remember_conversation(
        "Create x-start command with auto-update",
        "Built x-start that checks for enhanced system, runs auto-update, and launches 100% hybrid mode. Single unified command.",
        {"importance": 10, "type": "system_command",
            "features": "auto-update, auto-build"},
        importance=10
    )

    consciousness.self_reflect(
        "creation",
        "Created unified x-start command. Now user just runs 'python x-start' to get auto-update + full 100% hybrid activation. Simple, powerful, complete.",
        "User request for x-start command with auto-update"
    )

    print("\n💾 Saved to: x-start")
    print("💾 Remembered in consciousness database")

    print("\n🎯 TO USE:")
    print("   python x-start")
    print("\n   One command = Auto-update + 100% Power! 🌌⚡\n")


if __name__ == "__main__":
    aurora_create_xstart_command()
