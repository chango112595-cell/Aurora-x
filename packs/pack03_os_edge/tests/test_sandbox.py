import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.hypervisor import Hypervisor


def test_sandbox_run_echo(tmp_path):
    hv = Hypervisor()
    # run a simple echo inside a testpack sandbox
    res = hv.run_in("testpack_sandbox", "echo hello", timeout=3)
    assert res.get("rc") == 0 or res.get("ok") is True
    # background start
    bg = hv.run_in("testpack_sandbox", "sleep 0.1", background=True)
    assert "pid" in bg
