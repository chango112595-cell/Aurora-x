#!/usr/bin/env python3
"""Quick emoji fixer for luminar_nexus.py"""
import re

EMOJI_MAP = {
    '✅': '[OK]',
    '✓': '[+]',
    '🌌': '[AURORA]',
    '⚠️': '[WARN]',
    '❌': '[ERROR]',
    '→': '->',
}

filepath = 'tools/luminar_nexus.py'
with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

for emoji, replacement in EMOJI_MAP.items():
    content = content.replace(emoji, replacement)

# Fallback regex for any remaining unicode emojis
content = re.sub(r'[\U0001F300-\U0001F9FF]', '[EMOJI]', content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'[AURORA] Fixed {filepath} - All emojis replaced!')
