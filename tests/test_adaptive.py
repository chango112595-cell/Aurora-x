"""Lightweight smoke tests for CI quick check."""
from aurora_x.app_settings import SETTINGS


def test_app_settings_loads():
    assert SETTINGS is not None
    assert hasattr(SETTINGS, "port")
    assert hasattr(SETTINGS, "t08_enabled")
    assert hasattr(SETTINGS, "ui")
