#!/bin/bash

echo "🔧 Committing and pushing Luminar Nexus fixes..."

cd /workspaces/Aurora-x

# Create new branch
git checkout -b draft/luminar-nexus-fixes

# Add changes
git add tools/luminar_nexus.py tools/aurora_process_grandmaster.py

# Commit
git commit -m "Fix Luminar Nexus subprocess issues

- Replace capture_output=True with stdout/stderr=PIPE
- Fixes ValueError conflicts with subprocess parameters
- Maintains all of Aurora's original logic and structure
- Added dependency installation and health monitoring"

# Push to remote
git push -u origin draft/luminar-nexus-fixes

echo "✅ Changes pushed to draft/luminar-nexus-fixes"
