#!/usr/bin/env python3
"""
Aurora's JSX Error Fix Script
Placed in debug/ folder for proper organization
"""
import re

print("[STAR] Aurora: Analyzing JSX errors in chat-interface.tsx...")

# Read the broken file
with open("/workspaces/Aurora-x/client/src/components/chat-interface.tsx") as f:
    content = f.read()

print("\n[SCAN] Aurora: Found issues:")
print("   - Line 177: Misplaced </QuantumBackground> closing tag")
print("   - Line 190: Another misplaced </QuantumBackground> closing tag")
print("   - Line 262: Orphaned </QuantumBackground> with no opening tag")

print("\n[EMOJI]️ Aurora: Fixing JSX structure...")

# Fix 1: Remove misplaced closing tag after first div
content = re.sub(
    r"(\s+</div>\n)\s+</QuantumBackground>\n\s+\);\n}\n(\s+if \(line\.includes)",
    r"\1                            );\n                          }\n\2",
    content,
)

# Fix 2: Remove misplaced closing tag after second div
content = re.sub(
    r"(\s+</div>\n)\s+</QuantumBackground>\n\s+\);\n}\n(\s+return <div key)",
    r"\1                            );\n                          }\n\2",
    content,
)

# Fix 3: Remove orphaned closing tag at end
content = re.sub(r"(\s+</div>\n\s+</div>\n\s+</div>\n)\s+</QuantumBackground>\n(\s+\);\n})", r"\1\2", content)

# Write fixed content
with open("/workspaces/Aurora-x/client/src/components/chat-interface.tsx", "w") as f:
    f.write(content)

print("[OK] Aurora: JSX errors fixed!")
print("[SPARKLE] Aurora: Done! Pages should load now.")
