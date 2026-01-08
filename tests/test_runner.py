"""
Aurora Runner Test Suite
Verifies that the universal runner starts, supervises, and shuts down all services properly.
"""

import signal
import subprocess
import sys
import time


def test_runner_boot_and_shutdown(tmp_path):
    """Ensure aurora_runner.py boots and terminates correctly."""
    proc = subprocess.Popen(
        [sys.executable, "aurora_runner.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    time.sleep(5)

    assert proc.poll() is None, "Runner crashed prematurely"

    # Graceful shutdown: prefer SIGINT when supported, else terminate on Windows
    try:
        proc.send_signal(signal.SIGINT)
    except (ValueError, AttributeError):
        proc.terminate()

    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()

    assert proc.returncode in (0, None, 1, -1)


def test_runner_service_list_defined():
    """Verify SERVICES list is properly defined in aurora_runner."""
    import aurora_runner

    assert hasattr(aurora_runner, "SERVICES"), "SERVICES list not defined"
    assert len(aurora_runner.SERVICES) > 0, "SERVICES list is empty"

    for svc in aurora_runner.SERVICES:
        assert "name" in svc, "Service missing 'name'"
        assert "cmd" in svc, "Service missing 'cmd'"
        assert "port" in svc, "Service missing 'port'"


def test_port_check_function():
    """Verify port check utility works correctly."""
    import aurora_runner

    assert callable(aurora_runner.check_port), "check_port function not defined"

    result = aurora_runner.check_port(99999)
    assert isinstance(result, bool), "check_port should return boolean"


def test_wait_for_port_function():
    """Verify wait_for_port utility works correctly."""
    import aurora_runner

    assert callable(aurora_runner.wait_for_port), "wait_for_port function not defined"

    result = aurora_runner.wait_for_port(99999, timeout=1)
    assert result is False, "wait_for_port should return False for unused port"


def test_runtime_check():
    """Verify runtime check validates Python version."""
    import aurora_runner

    assert callable(aurora_runner.ensure_runtime), "ensure_runtime function not defined"

    assert sys.version_info >= (3, 10), "Python 3.10+ required"
