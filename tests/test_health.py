#!/usr/bin/env python3
"""Integration tests for health and readiness endpoints."""

import os
from fastapi.testclient import TestClient
from aurora_x.serve import app

# Allow tests to run without secrets
os.environ.setdefault("AURORA_ALLOW_MISSING_SECRETS", "1")

client = TestClient(app)


def test_readyz_exists():
    resp = client.get("/readyz")
    assert resp.status_code in (200, 503)
    data = resp.json()
    assert "config_ok" in data
    assert "dependencies" in data


def test_healthz_exists():
    resp = client.get("/healthz")
    assert resp.status_code == 200


def test_metrics_endpoint():
    resp = client.get("/metrics")
    assert resp.status_code == 200
    # Content can be Prometheus or fallback text; ensure non-empty
    assert resp.text.strip() != ""
