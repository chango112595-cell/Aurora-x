import os
import time

import httpx

BASE = os.getenv("HOST", "http://127.0.0.1:8000")


def test_health_endpoint():
    deadline = time.time() + 15
    last_exc = None
    while time.time() < deadline:
        try:
            r = httpx.get(f"{BASE}/healthz", timeout=5)
            assert r.status_code == 200, r.text
            txt = r.text.lower()
            if "ok" in txt or "healthy" in txt:
                return
            try:
                data = r.json()
                if isinstance(data, dict):
                    status = str(data.get("status", "")).lower()
                    assert "ok" in status or "healthy" in status
                return
            except Exception:
                return
        except Exception as e:
            last_exc = e
            time.sleep(1)
    raise AssertionError(f"/healthz did not respond as expected: {last_exc}")
