#!/usr/bin/env python3
"""
Aurora Autonomous Fix: Remove all Unicode emojis from Luminar Nexus V2
to fix Windows encoding issues
"""

from pathlib import Path


def remove_emojis_from_file(file_path):
    """Remove emoji characters from print statements"""
    content = file_path.read_text(encoding='utf-8')

    # Map emojis to ASCII replacements
    emoji_replacements = {
        '✅': '[OK]',
        '❌': '[ERROR]',
        '⚠️': '[WARN]',
        '🌌': '',
        '🔗': '[LINK]',
        '🔍': '[SCAN]',
        '🚀': '[START]',
        '✨': '[FEATURES]',
        '🔧': '[FIX]',
        '📊': '[STATS]',
        'ℹ️': '[INFO]',
        '•': '-',
        '🎯': '[TARGET]',
        '💬': '[CHAT]',
    }

    modified = content
    for emoji, replacement in emoji_replacements.items():
        modified = modified.replace(emoji, replacement)

    # Write back
    file_path.write_text(modified, encoding='utf-8')
    print(f"[Aurora] Fixed encoding in {file_path.name}")


if __name__ == "__main__":
    print("[Aurora] Autonomous fix: Removing emojis from Luminar Nexus V2")
    print("[Aurora] This fixes Windows cp1252 encoding errors\n")

    luminar_file = Path("tools/luminar_nexus_v2.py")
    if luminar_file.exists():
        remove_emojis_from_file(luminar_file)
        print("\n[Aurora] Fix complete! Luminar Nexus V2 ready for Windows.")
    else:
        print("[ERROR] Luminar Nexus V2 file not found")
