#!/usr/bin/env python3
"""Start and keep Bridge service running"""

import subprocess
import time
import sys

def start_bridge():
    """Start the Bridge service"""
    print("🚀 Starting Aurora-X Factory Bridge on port 5001...")
    
    # Run the Bridge service
    proc = subprocess.Popen(
        [sys.executable, "aurora_x/bridge/service.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    print(f"Bridge started with PID: {proc.pid}")
    
    # Keep it running and show output
    try:
        while True:
            line = proc.stdout.readline()
            if line:
                print(line.strip())
            
            # Check if process is still running
            if proc.poll() is not None:
                print(f"Bridge process exited with code: {proc.returncode}")
                break
                
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nShutting down Bridge service...")
        proc.terminate()
        proc.wait(timeout=5)

if __name__ == "__main__":
    start_bridge()