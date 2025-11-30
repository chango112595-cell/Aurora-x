#!/usr/bin/env python3
"""
Safe perf tests: quick CPU and disk micro-benchmarks that are low intensity.
Deep benchmarks are gated behind explicit operator approval and an 'allow_deep' flag.
"""
import time, os, tempfile, argparse
from pathlib import Path

def cpu_test(iterations=200000):
    s = time.time()
    x = 0
    for i in range(iterations):
        x += (i * 3) ^ (i << 1)
    return time.time() - s

def io_test(size_mb=10):
    d = tempfile.mkdtemp()
    path = Path(d) / "tmp_io_test.bin"
    s = time.time()
    with open(path, "wb") as f:
        f.write(b"\0" * (1024 * 1024 * size_mb))
    dur = time.time() - s
    try:
        path.unlink()
    except Exception:
        pass
    return dur

def deep_cpu_stress(duration=5):
    # short stress loop - runs only if operator approved
    s = time.time()
    while time.time() - s < duration:
        sum(i*i for i in range(10000))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--deep", action="store_true", help="Run deep (operator approved) tests")
    args = p.parse_args()
    r = {"cpu_ms": cpu_test(), "io_s": io_test()}
    if args.deep:
        deep_cpu_stress(duration=3)
        r["deep_done"] = True
    print(r)
