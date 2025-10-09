#!/usr/bin/env python3
import os, urllib.request, json, sys
BASE = os.getenv("AURORA_BASE_URL", "http://localhost:5000")
paths = ["/dashboard/spec_runs", "/api/spec_runs"]
ok = True
for p in paths:
    try:
        with urllib.request.urlopen(BASE + p, timeout=10) as r:
            print(p, r.status)
            if p.endswith("/api/spec_runs"):
                data = json.loads(r.read().decode())
                print("runs:", len(data.get("runs", [])))
    except Exception as e:
        ok = False
        print("ERR", p, e)
print("Post-deploy check:", "OK" if ok else "FAILED")
sys.exit(0 if ok else 1)