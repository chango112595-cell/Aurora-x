"""
Aurora Module: Validator_0006
ID: 0006
Category: validator
Generated: 2025-12-08T11:39:12.489834Z
"""
import time

class Validator_0006Execute:
    def __init__(self, ctx=None):
        self.ctx = ctx or {}

    def execute(self, payload):
        start = time.time()
        try:
            data = payload.get("data", {})
            rules = payload.get("rules", [])
            errors = []
            for rule in rules:
                field = rule.get("field")
                required = rule.get("required", False)
                if required and field not in data:
                    errors.append(f"Missing required field: {field}")
            valid = len(errors) == 0
            return {"status": "ok", "valid": valid, "errors": errors, "duration_ms": (time.time()-start)*1000}
        except Exception as e:
            return {"status": "error", "error": str(e)}

def execute(payload=None):
    instance = Validator_0006Execute()
    return instance.execute(payload or {})
