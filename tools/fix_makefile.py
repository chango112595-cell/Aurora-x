#!/usr/bin/env python3
"""Fix Makefile tab/space issues while preserving heredocs."""

with open("Makefile") as f:
    lines = f.readlines()

fixed_lines = []
in_heredoc = False
heredoc_marker = None

for i, line in enumerate(lines):
    # Check for heredoc start
    if "python - <<" in line:
        in_heredoc = True
        heredoc_marker = line.split("<<")[-1].strip().strip("'")
        fixed_lines.append(line)
    # Check for heredoc end
    elif in_heredoc and line.strip() == heredoc_marker:
        in_heredoc = False
        heredoc_marker = None
        fixed_lines.append(line)
    # Inside heredoc - keep original formatting
    elif in_heredoc:
        fixed_lines.append(line)
    # Make command line that starts with 8 spaces - convert to tab
    elif line.startswith("        ") and i > 0 and ":" in lines[i - 1]:
        fixed_lines.append("\t" + line[8:])
    # Keep everything else as is
    else:
        fixed_lines.append(line)

with open("Makefile", "w") as f:
    f.writelines(fixed_lines)

print("Fixed Makefile tab/space issues while preserving heredocs")
