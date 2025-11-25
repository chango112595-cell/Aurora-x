# Fix Luminar Nexus V2 Python Paths - Completion Request

## Objective
Apply the same Python path fixes to luminar_nexus_v2.py that were successfully applied to luminar_nexus.py.

## Background
Just fixed in luminar_nexus.py (commit 41a211a27):
- **Problem**: Hardcoded `/workspaces/Aurora-x/env/bin/python3` doesn't exist
- **Solution**: Use `python3` which automatically finds `.venv`
- **Result**: All 5 services now running correctly

## Requirements

### 1. Locate Broken Paths in V2
Search `tools/luminar_nexus_v2.py` for:
- Any instances of `/workspaces/Aurora-x/env/bin/python3`
- Any instances of `/workspaces/Aurora-x/env/bin/python`
- Check server command templates for all Python services

### 2. Apply Fixes to V2
Update the command templates for these services:
- **Bridge Service**: Change Python path in command_template
- **Self-Learn Service**: Change Python path in command_template
- **Chat Service**: Change Python path in command_template

### 3. Ensure Consistency
Make sure V2 command templates match V1:
```python
# V1 (fixed):
"command_template": "cd /workspaces/Aurora-x && python3 -m aurora_x.bridge.service"
"command_template": "cd /workspaces/Aurora-x && python3 -c 'from aurora_x.self_learn_server import app; import uvicorn; uvicorn.run(app, host=\"0.0.0.0\", port={port})'"
"command_template": "cd /workspaces/Aurora-x && python3 -c 'from tools.luminar_nexus import run_chat_server; run_chat_server({port})'"
```

### 4. Implementation Steps
1. Read `tools/luminar_nexus_v2.py`
2. Use grep or search to find all hardcoded Python paths
3. Use autonomous_system to modify file (replace_string_in_file)
4. Update each broken path found
5. Verify all changes applied correctly

### 5. Verification
After fixes:
- Count replacements made (should be 3 for bridge, self-learn, chat)
- Verify no more hardcoded `/workspaces/Aurora-x/env/bin/python` paths remain
- Confirm V2 configuration matches V1

## Deliverables
1. Modified `tools/luminar_nexus_v2.py` with corrected Python paths
2. Report in `.aurora_knowledge/V2_PYTHON_PATH_FIX_REPORT.md`:
   - Number of paths fixed
   - Services updated
   - Verification that V2 ready for use

## Success Criteria
- All hardcoded Python paths in V2 replaced with system python3
- V2 configuration matches working V1 configuration
- File saved and changes ready for commit

## Aurora's Tools to Use
- Tier 28: Autonomous Tool Use (read files, modify code)
- Tier 13: File system operations
- autonomous_system.read_file() to read V2
- autonomous_system.replace_in_file() to fix paths
- Tier 29: Problem-solving to ensure all instances found

This is a critical fix to ensure V2 works when we switch to it (Task #6 in TODO list).
