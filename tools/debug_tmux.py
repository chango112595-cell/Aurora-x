#!/usr/bin/env python3

import subprocess

# Test simple tmux command
print("🐛 Testing basic tmux command...")

command = "cd /workspaces/Aurora-x && NODE_ENV=development npx tsx server/index.ts"
session = "test-backend"

print(f"🐛 Command: {command}")
print(f"🐛 Session: {session}")

# Kill any existing session
subprocess.run(['tmux', 'kill-session', '-t', session], 
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Try the command
full_command = f"tmux new-session -d -s {session} '{command}'"
print(f"🐛 Full command: {full_command}")

result = subprocess.run(full_command, shell=True, capture_output=True, text=True)

print(f"🐛 Return code: {result.returncode}")
print(f"🐛 stdout: '{result.stdout}'")
print(f"🐛 stderr: '{result.stderr}'")

# Check if session exists
check_result = subprocess.run(['tmux', 'list-sessions'], capture_output=True, text=True)
print(f"🐛 Sessions: {check_result.stdout}")