# Aurora-X Health Endpoint Tests (SPEC-5)
"""Smoke tests for /healthz endpoint"""

import os

import httpx


def test_healthz():
    """Test that /healthz endpoint returns 200 and correct status"""
    host = os.getenv("HOST", "http://127.0.0.1:8000")
    r = httpx.get(f"{host}/healthz", timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert "ok" in data or data.get("status") == "ok" or data.get("status") == "healthy"


def test_healthz_response_structure():
    """Test that /healthz returns expected structure"""
    host = os.getenv("HOST", "http://127.0.0.1:8000")
    r = httpx.get(f"{host}/healthz", timeout=5)
    assert r.status_code == 200
    data = r.json()
    # Should have at least 'ok' or 'status' field
    assert isinstance(data, dict)
    assert "ok" in data or "status" in data
