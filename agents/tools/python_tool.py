#!/usr/bin/env python3
"""
A small, time-limited Python runner. For production use containers or restricted interpreters.
"""
import time, traceback
def python_run(params):
    code = params.get("code","")
    # very naive sandbox: do not use in real world without stricter controls
    gl = {}
    loc = {}
    start = time.time()
    try:
        exec(code, gl, loc)
        return {"ok": True, "result": loc.get("result"), "elapsed": time.time()-start}
    except Exception as e:
        return {"ok": False, "error": str(e), "trace": traceback.format_exc()}
