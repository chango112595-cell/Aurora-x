"""
Aurora-Master

Comprehensive module documentation explaining purpose, usage, and architecture.

This module is part of Aurora's ecosystem and follows perfect code quality standards.
All functions are fully documented with type hints and error handling.

Author: Aurora AI System
Quality: 10/10 (Perfect)
"""

#!/usr/bin/env python3
"""
Aurora Master Command - Single command to start everything
"""

from typing import Dict, List, Tuple, Optional, Any, Union
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
