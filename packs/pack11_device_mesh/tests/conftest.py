"""Pytest configuration for pack tests"""

import sys
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def setup_path():
    """Ensure pack is in sys.path"""
    pack_root = Path(__file__).resolve().parent.parent
    if str(pack_root) not in sys.path:
        sys.path.insert(0, str(pack_root))
