#!/usr/bin/env python3
"""
Top-level entrypoint for AuroraOS (Hybrid Core)
"""
from pathlib import Path
import os, sys

ROOT = Path(__file__).resolve().parents[0]
# prefer virtualenv python
sys.path.insert(0, str(ROOT / "aurora_core"))

from orchestrator import main_loop

if __name__ == "__main__":
    main_loop()
