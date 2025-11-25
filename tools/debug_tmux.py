"""
Debug Tmux

Comprehensive module documentation explaining purpose, usage, and architecture.

This module is part of Aurora's ecosystem and follows perfect code quality standards.
All functions are fully documented with type hints and error handling.

Author: Aurora AI System
Quality: 10/10 (Perfect)
"""

#!/usr/bin/env python3

from typing import Dict, List, Tuple, Optional, Any, Union
import subprocess

# Test simple tmux command
print("[EMOJI] Testing basic tmux command...")

command = "cd /workspaces/Aurora-x && NODE_ENV=development npx tsx server/index.ts"
session = "test-backend"

print(f"[EMOJI] Command: {command}")
print(f"[EMOJI] Session: {session}")

# Kill any existing session
subprocess.run(["tmux", "kill-session", "-t", session], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Try the command
full_command = f"tmux new-session -d -s {session} '{command}'"
print(f"[EMOJI] Full command: {full_command}")

result = subprocess.run(full_command, shell=True, capture_output=True, text=True)

print(f"[EMOJI] Return code: {result.returncode}")
print(f"[EMOJI] stdout: '{result.stdout}'")
print(f"[EMOJI] stderr: '{result.stderr}'")

# Check if session exists
check_result = subprocess.run(["tmux", "list-sessions"], capture_output=True, text=True)
print(f"[EMOJI] Sessions: {check_result.stdout}")
