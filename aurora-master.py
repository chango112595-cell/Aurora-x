#!/usr/bin/env python3
"""
Aurora Master Command - Single command to start everything
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Start all Aurora services"""
    workspace = Path("/workspaces/Aurora-x")
    luminar_cmd = [sys.executable, str(workspace / "tools" / "luminar_nexus.py"), "start-all"]

    # Change to workspace directory
    import os

    os.chdir(workspace)

    # Run Luminar Nexus start-all
    result = subprocess.run(luminar_cmd, check=False)

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
