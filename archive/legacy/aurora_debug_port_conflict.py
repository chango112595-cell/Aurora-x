#!/usr/bin/env python3
"""
Aurora Debug Task: Port 5001 Conflict Analysis
Aurora must diagnose and decide how to fix the port conflict
"""

import json
from datetime import datetime
from pathlib import Path

AURORA_DEBUG_TASK = """
🤖 AURORA DEBUG TASK: PORT 5001 CONFLICT
==========================================

Problem: When you run `python3 -m aurora_x.serve`, port 5001 shows backend API JSON
Expected: Port 5001 should show the Vite UI (HTML frontend)

Current Architecture:
- Luminar Nexus wants Vite on port 5001 ✓ (correct)
- But `aurora_x/serve.py` also wants port 5001 ✗ (conflict!)

Questions for Aurora to Answer:
1. What does `aurora_x/serve.py` actually do?
2. What port does it default to?
3. Is there a Node.js backend server (server/index.ts)?
4. What's the relationship between serve.py and the Node.js server?

Files to Investigate:
- /workspaces/Aurora-x/aurora_x/serve.py (lines 600-630, check the port logic)
- /workspaces/Aurora-x/server/index.ts (is this the real backend?)
- /workspaces/Aurora-x/AURORA_X_COMPLETE_PROJECT.md (architecture docs)

Clues:
- Luminar Nexus runs: `npx tsx server/index.ts` on port 5000 (Node.js backend)
- serve.py runs a FastAPI server with routes like /api/chat, /api/solve, etc.
- These might be TWO DIFFERENT servers, or one might be redundant

Your Task:
1. Analyze: What's the role of serve.py vs the Node.js server?
2. Decide: Should serve.py run on a different port? Or should it be removed?
3. Implement: Fix the conflict
4. Test: Verify port 5001 shows HTML (Vite UI), not JSON (API)
5. Commit: Explain your reasoning

Think about it, Aurora. What's your diagnosis? 🔍
"""

print(AURORA_DEBUG_TASK)

# Log this task
log_file = Path("/workspaces/Aurora-x/.aurora_knowledge/aurora_debug_task.jsonl")
log_file.parent.mkdir(exist_ok=True)

with open(log_file, "a") as f:
    entry = {
        "timestamp": datetime.now().isoformat(),
        "task": "Port 5001 Conflict Resolution",
        "status": "INVESTIGATING",
        "problem": "serve.py and Luminar Nexus both want port 5001",
        "expected": "Port 5001 = Vite UI (HTML), Port 5000 = Backend API (JSON)",
    }
    f.write(json.dumps(entry) + "\n")

print("\n📋 Task logged to: /workspaces/Aurora-x/.aurora_knowledge/aurora_debug_task.jsonl")
print("⏳ Aurora is investigating...\n")
