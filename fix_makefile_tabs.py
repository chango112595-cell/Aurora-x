#!/usr/bin/env python3
"""Fix Makefile indentation: convert spaces to tabs for command lines"""

# Read the current Makefile
with open("Makefile") as f:
    lines = f.readlines()

# Fix indentation: convert 8 spaces or any leading spaces to tabs for command lines
fixed_lines = []
for line in lines:
    # Check if line starts with spaces (likely a command line)
    if line.startswith("        "):  # 8 spaces
        # Replace leading 8 spaces with a tab
        fixed_line = "\t" + line.lstrip(" ")
        fixed_lines.append(fixed_line)
    elif line.startswith("    ") and not line.startswith("\t"):  # 4+ spaces but not a tab
        # Count leading spaces and replace with appropriate tabs
        spaces = len(line) - len(line.lstrip(" "))
        tabs = spaces // 8 + (1 if spaces % 8 else 0)
        fixed_line = "\t" * tabs + line.lstrip(" ")
        fixed_lines.append(fixed_line)
    else:
        # Keep the line as is
        fixed_lines.append(line)

# Write back the fixed Makefile
with open("Makefile", "w") as f:
    f.writelines(fixed_lines)

print("✅ Fixed Makefile indentation (converted spaces to tabs)")
print("   Total lines processed:", len(lines))
print("\nTest the fix:")
print("  make help")
print("  make demo-list")
print("  make demo-all")
