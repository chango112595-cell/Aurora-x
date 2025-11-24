#!/usr/bin/env python3
"""
Aurora Device Demo Simple - Basic version without complex dependencies
"""

import sys
from pathlib import Path

# Add tools directory to path
tools_dir = Path(__file__).parent / "tools"
sys.path.insert(0, str(tools_dir))

try:
    from aurora_expert_knowledge import AuroraExpertKnowledge

    expert_available = True
except ImportError:
    expert_available = False
    print("[WARN] Aurora Expert Knowledge module not found - running in basic mode")


def main():
    """Simple demonstration"""
    print("[LAUNCH] Aurora Device Demo (Simple Version)")
    print("=" * 50)

    if expert_available:
        aurora_expert = AuroraExpertKnowledge()
        print(f"[OK] Aurora Expert Knowledge loaded with {len(aurora_expert.languages)} languages")
    else:
        print("[WARN] Running in basic mode without expert knowledge")

    print()
    print("[EMOJI] Device Programming Examples:")
    print("• iOS/macOS: AppleScript, Swift, Objective-C")
    print("• Android: Kotlin, Java")
    print("• IoT: Arduino, ESP32, Raspberry Pi")
    print("• Automation: Bash, PowerShell, Python")
    print("• Cloud: Docker, Kubernetes")
    print()
    print("[EMOJI] Aurora is ready for device programming tasks!")


if __name__ == "__main__":
    main()
