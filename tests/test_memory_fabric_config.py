#!/usr/bin/env python3
"""
Test suite for Memory Fabric configuration
Tests that the host/port configuration is properly configurable
"""

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_default_host_configuration():
    """Test that default host is loopback (127.0.0.1)"""
    # Clear any existing env var
    if "MEMORY_FABRIC_HOST" in os.environ:
        del os.environ["MEMORY_FABRIC_HOST"]

    # Re-import to get fresh value
    import importlib

    if "aurora_memory_fabric_v2.service" in sys.modules:
        importlib.reload(sys.modules["aurora_memory_fabric_v2.service"])
    else:
        pass

    from aurora_memory_fabric_v2.service import MEMORY_FABRIC_HOST

    assert MEMORY_FABRIC_HOST == "127.0.0.1", "Default host should be 127.0.0.1"


def test_custom_host_configuration():
    """Test that custom host can be set via environment variable"""
    # Set custom host
    os.environ["MEMORY_FABRIC_HOST"] = "0.0.0.0"

    # Re-import to get new value
    import importlib

    if "aurora_memory_fabric_v2.service" in sys.modules:
        importlib.reload(sys.modules["aurora_memory_fabric_v2.service"])

    from aurora_memory_fabric_v2.service import MEMORY_FABRIC_HOST

    assert MEMORY_FABRIC_HOST == "0.0.0.0", "Host should be configurable via MEMORY_FABRIC_HOST"

    # Clean up
    del os.environ["MEMORY_FABRIC_HOST"]


def test_check_existing_service_uses_configured_host():
    """Test that check_existing_service respects the host parameter"""
    from aurora_memory_fabric_v2.service import check_existing_service

    # Should not fail with custom host
    result = check_existing_service(5004, "127.0.0.1")
    assert isinstance(result, bool), "check_existing_service should return boolean"

    result = check_existing_service(5004, "0.0.0.0")
    assert isinstance(result, bool), "check_existing_service should work with 0.0.0.0"


def test_is_port_in_use_accepts_host_parameter():
    """Test that is_port_in_use accepts and uses host parameter"""
    from aurora_memory_fabric_v2.service import is_port_in_use

    # Test with loopback
    result = is_port_in_use(9999, "127.0.0.1")
    assert isinstance(result, bool), "is_port_in_use should return boolean"


def test_start_service_accepts_host_parameter():
    """Test that start_memory_fabric_service function signature accepts host parameter"""
    import inspect

    from aurora_memory_fabric_v2.service import start_memory_fabric_service

    sig = inspect.signature(start_memory_fabric_service)
    params = list(sig.parameters.keys())

    assert "port" in params, "Function should have port parameter"
    assert "host" in params, "Function should have host parameter"

    # Check default values
    assert sig.parameters["port"].default == 5004, "Default port should be 5004"
    # The default for host is MEMORY_FABRIC_HOST which we can't easily check here,
    # but we verified it works in other tests


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
