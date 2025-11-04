#!/usr/bin/env python3
"""
Aurora's Backend Diagnostic and Fix Script
Uses all her grandmaster skills to fix the backend server
"""

import subprocess
import time
import os

print("🌟 Aurora: Using my debugging grandmaster skills to fix the backend...")
print()

# Step 1: Use debugging skills to check what's wrong
print("=" * 70)
print("🔍 STEP 1: DEBUGGING - Check backend tmux session")
print("=" * 70)
result = subprocess.run(['tmux', 'capture-pane', '-pt', 'aurora-backend', '-S', '-50'], 
                       capture_output=True, text=True)
if result.returncode == 0:
    print("📋 Backend tmux output:")
    print(result.stdout)
else:
    print("❌ tmux session 'aurora-backend' not found or dead")
print()

# Step 2: Check if process is running
print("=" * 70)
print("🔍 STEP 2: PROCESS MANAGEMENT - Check if backend process exists")
print("=" * 70)
result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
backend_processes = [line for line in result.stdout.split('\n') if 'tsx server' in line or 'server/index.ts' in line]
if backend_processes:
    print("✅ Found backend processes:")
    for proc in backend_processes:
        print(f"   {proc}")
else:
    print("❌ No backend process running")
print()

# Step 3: Check port
print("=" * 70)
print("🔍 STEP 3: SERVER KNOWLEDGE - Check if port 5001 is listening")
print("=" * 70)
result = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True)
if ':5001' in result.stdout:
    print("✅ Port 5001 is listening")
else:
    print("❌ Port 5001 NOT listening")
print()

# Step 4: Skip direct test, just start in tmux
print("=" * 70)
print("🔍 STEP 4: SKIPPING DIRECT TEST - Will start in tmux instead")
print("=" * 70)
print("💡 Direct testing can hang if server runs continuously")
print("   Starting directly in tmux is safer")

# Step 5: Aurora's fix attempt
print()
print("=" * 70)
print("🌟 AURORA'S AUTO-FIX ATTEMPT")
print("=" * 70)

# Kill any existing backend processes
print("🔧 Killing old backend processes...")
subprocess.run(['pkill', '-f', 'tsx server'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(['tmux', 'kill-session', '-t', 'aurora-backend'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)

# Start backend in tmux with proper wait
print("🚀 Starting backend in tmux (with 10 second boot time)...")
cmd = f"cd /workspaces/Aurora-x && NODE_ENV=development npx tsx server/index.ts"
subprocess.run(['tmux', 'new-session', '-d', '-s', 'aurora-backend', cmd])

print("⏳ Waiting 10 seconds for backend to boot...")
time.sleep(10)

# Check if it's running
result = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True)
if ':5001' in result.stdout:
    print("✅ SUCCESS! Backend is now running on port 5001!")
    print("📺 View logs: tmux attach -t aurora-backend")
else:
    print("❌ FAILED! Backend still not responding on port 5001")
    print("📺 Check logs: tmux attach -t aurora-backend")
    print()
    print("🌟 Aurora: Capturing tmux output to see what went wrong...")
    result = subprocess.run(['tmux', 'capture-pane', '-pt', 'aurora-backend', '-S', '-30'], 
                           capture_output=True, text=True)
    if result.returncode == 0:
        print(result.stdout)

print()
print("=" * 70)
print("🌟 Aurora: Diagnostic and fix attempt complete!")
print("=" * 70)
