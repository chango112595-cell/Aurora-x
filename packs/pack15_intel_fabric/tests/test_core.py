"""Tests for pack15_intel_fabric core module"""

import sys
from pathlib import Path

import pytest

# Add pack to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.module import execute, health_check, info, initialize, shutdown


class TestCoreModule:
    def test_info_returns_dict(self):
        result = info()
        assert isinstance(result, dict)
        assert "pack" in result
        assert result["pack"] == "pack15_intel_fabric"
        assert "version" in result
        assert "ts" in result

    def test_health_check_returns_bool(self):
        result = health_check()
        assert isinstance(result, bool)

    def test_initialize(self):
        result = initialize()
        assert result is True

    def test_shutdown(self):
        result = shutdown()
        assert result is True

    def test_execute_command(self):
        result = execute("test_command", {"param1": "value1"})
        assert result["status"] == "ok"
        assert result["command"] == "test_command"
        assert result["params"] == {"param1": "value1"}


class TestIPC:
    def test_send_request(self):
        from core.ipc import send_request

        req_id = send_request("test_target", "test_action", {"key": "value"})
        assert req_id is not None
        assert len(req_id) > 0

    def test_broadcast(self):
        from core.ipc import broadcast

        result = broadcast("test_event", {"data": "test"})
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
