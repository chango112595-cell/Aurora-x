#!/usr/bin/env python3
from pathlib import Path

from aurora_x.spec.parser_v3 import parse_v3
from aurora_x.synthesis.flow_ops import impl_for


def main(spec_path: str):
    sp = Path(spec_path)
    md = sp.read_text(encoding="utf-8")
    spec = parse_v3(md)
    import json as _J
    import time
    run_id = time.strftime("run-%Y%m%d-%H%M%S")
    out = Path("runs") / run_id
    (out / "src").mkdir(parents=True, exist_ok=True)
    (out / "tests").mkdir(parents=True, exist_ok=True)

    test_lines = ["import unittest"]
    for fn in spec.functions:
        code = impl_for(fn.signature, fn.description)
        modname = fn.name
        (out / "src" / f"{modname}.py").write_text(code, encoding="utf-8")
        test_lines.append(f"from src.{modname} import {modname}")
        for i, ex in enumerate(fn.examples or []):
            args = ", ".join(f"{k}={repr(v)}" for k,v in ex.inputs.items())
            test_lines.append(f"class Test_{modname}_{i}(unittest.TestCase):\n    def test_{i}(self):\n        self.assertEqual({modname}({args}), {repr(ex.output)})")

    test_lines.append("\nif __name__=='__main__': unittest.main()")
    (out / "tests" / "test_v3.py").write_text("\n".join(test_lines), encoding="utf-8")
    (out / "report.html").write_text(f"<h2>Aurora-X v3 Report</h2><p>Run: {run_id}</p>", encoding="utf-8")

    row = {
        "run_id": out.name,
        "spec": sp.name,
        "ok": True,
        "report": f"/{out}/report.html",
        "bias": None,
        "spark": None
    }
    log = Path("runs") / "spec_runs.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as f:
        f.write(_J.dumps(row) + "\n")

    try:
        from aurora_x.serve_dashboard_v2 import record_run
        record_run(out.name, sp.name, True, f"/{out}/report.html")
    except Exception:
        pass

    print(f"[OK] v3 generated: {out}")
    print(" - Source:", out / "src")
    print(" - Tests: ", out / "tests")
    print(" - Report:", out / "report.html")
    print(f"Run tests: python -m unittest discover -s {out/'tests'} -t {out}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python tools/spec_compile_v3.py <spec.md>"); exit(1)
    main(sys.argv[1])
