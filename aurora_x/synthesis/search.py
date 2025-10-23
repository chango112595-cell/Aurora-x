from __future__ import annotations

import time
from pathlib import Path

from aurora_x.spec.parser_v2 import RichSpec
from aurora_x.synthesis.templates_py import generate_impl


def synthesize(spec: RichSpec, runs_dir: Path) -> Path:
    run_id = time.strftime("run-%Y%m%d-%H%M%S")
    out = runs_dir / run_id
    (out / "src").mkdir(parents=True, exist_ok=True)
    (out / "tests").mkdir(parents=True, exist_ok=True)
    impl = generate_impl(spec.signature, spec.description)
    (out / "src" / f"{spec.title}.py").write_text(impl, encoding="utf-8")

    # tests
    t = ["import unittest", f"from src.{spec.title} import {spec.title}"]
    for i, ex in enumerate(spec.examples):
        args = ", ".join(f"{k}={repr(v)}" for k, v in ex.inputs.items())
        t.append(
            f"class T{i}(unittest.TestCase):\n    def test_{i}(self):\n        self.assertEqual({spec.title}({args}), {repr(ex.output)})"
        )
    t.append("if __name__=='__main__': unittest.main()")
    (out / "tests" / f"test_{spec.title}.py").write_text("\n".join(t), encoding="utf-8")

    (out / "report.html").write_text(f"<h3>{spec.title}</h3><p>Generated at {run_id}</p>", encoding="utf-8")
    return out
