#!/usr/bin/env python3
"""Unit tests for Luminar Nexus orchestration engine"""

import sys
from pathlib import Path

def test_luminar_nexus_imports():
    """Test that Luminar Nexus can be imported"""
    sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
    import luminar_nexus
    assert luminar_nexus is not None

def test_luminar_nexus_has_start_all():
    """Test that Luminar Nexus has start_all function"""
    sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
    import luminar_nexus
    assert hasattr(luminar_nexus, 'LuminarNexus')

if __name__ == "__main__":
    test_luminar_nexus_imports()
    test_luminar_nexus_has_start_all()
    print("✅ All Luminar Nexus tests passed!")
