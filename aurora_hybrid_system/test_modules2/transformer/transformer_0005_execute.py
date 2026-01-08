"""
Aurora Module: Transformer_0005
ID: 0005
Category: transformer
Generated: 2025-12-08T11:38:50.015942Z
"""

import time


class Transformer_0005Execute:
    def __init__(self, ctx=None):
        self.ctx = ctx or {}

    def execute(self, payload):
        start = time.time()
        try:
            source = payload.get("source", {})
            mapping = payload.get("mapping", {})
            transformed = (
                {mapping.get(k, k): v for k, v in source.items()}
                if isinstance(source, dict)
                else source
            )
            return {
                "status": "ok",
                "transformed": transformed,
                "duration_ms": (time.time() - start) * 1000,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


def execute(payload=None):
    instance = Transformer_0005Execute()
    return instance.execute(payload or {})
