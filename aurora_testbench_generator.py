#!/usr/bin/env python3
# aurora_testbench_generator.py
# Generates the end-to-end test runner run_all_tests.py and supporting utilities.

import textwrap

from aurora_build_utils import TESTBENCH_DIR, log, safe_write

RUNNER = TESTBENCH_DIR / "run_all_tests.py"
RUNNER_CODE = textwrap.dedent('''
#!/usr/bin/env python3
"""run_all_tests.py - orchestrates staging, install, start, health, and pytest for all packs."""
import subprocess, sys, os, time
from pathlib import Path

ROOT = Path.cwd()
PACKS = sorted([p.name for p in (ROOT/'packs').iterdir() if p.is_dir() and p.name.startswith('pack')])

def sh(cmd, check=True, capture=False):
    print(f"> {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    if res.returncode != 0 and check:
        print('FAILED:', cmd)
        print(res.stdout)
        print(res.stderr)
    return res

def stage_pack(pack):
    return sh(f"python3 installer/aurora_installer.py stage --pack {pack}")

def dryrun_pack(pack):
    return sh(f"python3 installer/aurora_installer.py dry-run --pack {pack}")

def install_pack(pack):
    return sh(f"python3 installer/aurora_installer.py install --pack {pack}")

def start_pack(pack):
    p = Path('packs') / pack
    start = p / 'start.sh'
    if start.exists():
        return sh(f"bash {start}")
    return None

def stop_pack(pack):
    p = Path('packs') / pack
    stop = p / 'stop.sh'
    if stop.exists():
        return sh(f"bash {stop}")

def health_pack(pack):
    p = Path('packs') / pack
    health = p / 'health_check.sh'
    if health.exists():
        return sh(f"bash {health}")

def test_pack(pack):
    return sh(f"python3 -m pytest packs/{pack}/tests -q", check=False)

def run_all():
    summary = {}
    for pack in PACKS:
        print('\\n=== PACK:', pack, '===')
        stage_pack(pack)
        dryrun_pack(pack)
        install_pack(pack)
        start_pack(pack)
        time.sleep(0.2)
        health_pack(pack)
        res = test_pack(pack)
        summary[pack] = (res.returncode == 0)
        stop_pack(pack)
    print('\\n=== SUMMARY ===')
    for p, ok in summary.items():
        print(p, 'OK' if ok else 'FAIL')
    return summary

if __name__ == '__main__':
    run_all()
''').strip()


def main():
    safe_write(RUNNER, RUNNER_CODE, exe=True)
    log(f"Generated test runner at {RUNNER}")
    safe_write(
        TESTBENCH_DIR / "README.md",
        "Run: python3 run_all_tests.py from this directory",
        exe=False,
        backup=False,
    )
    log("Testbench generation complete.")


if __name__ == "__main__":
    main()
