#!/usr/bin/env python3
"""
import time
Aurora Self-Fix Task: Port Configuration Consolidation
Aurora must implement her own architecture decision
"""

import json
from datetime import datetime
from pathlib import Path

# Task for Aurora
AURORA_TASK = """
[AGENT] AURORA SELF-FIX TASK
========================

Your Decision: Consolidate to 2 main services
- Port 5000: Backend API (Node.js/tsx)
- Port 5001: Vite UI (moved from 5173)
- Port 5002: Self-Learn (optional, on-demand)
- Bridge: Optional (can be endpoint on backend)

Your Implementation Steps:
1. Edit /workspaces/Aurora-x/tools/luminar_nexus.py
2. Update servers config to:
   - Remove Bridge service (5001)
   - Remove Self-Learn from auto-start
   - Move Vite to port 5001
3. Update auto-start in /workspaces/Aurora-x/aurora_x/serve.py if needed
4. Test the new configuration
5. Commit with clear reasoning
6. Report results: what you changed and why

Current Status: Backend, Vite, Bridge, and Self-Learn all running
Expected Status After Fix: Only Backend (5000) and UI (5001)

Go ahead, Aurora. You've got this. [LAUNCH]
"""

print(AURORA_TASK)

# Log this task for Aurora
log_file = Path("/workspaces/Aurora-x/.aurora_knowledge/self_fix_task.jsonl")
log_file.parent.mkdir(exist_ok=True)

with open(log_file, "a", encoding="utf-8") as f:
    entry = {
        "timestamp": datetime.now().isoformat(),
        "task": "Port Configuration Consolidation",
        "status": "ASSIGNED",
        "description": "Move Vite to 5001, consolidate services, clean architecture",
        "expected_outcome": "Clean entry point with UI on 5001, API on 5000",
    }
    f.write(json.dumps(entry) + "\n")

print("\n[OK] Task assigned to Aurora")
print("[EMOJI] Task logged to: /workspaces/Aurora-x/.aurora_knowledge/self_fix_task.jsonl")
print("\n⏱️  Waiting for Aurora to implement...")
