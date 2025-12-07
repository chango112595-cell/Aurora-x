#!/usr/bin/env python3
import os
import tempfile
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.sandbox import run_in_sandbox


def test_sandbox_executes_simple_plugin():
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py") as f:
        f.write("print('hello world')\n")
        f.flush()
        path = f.name

    result = run_in_sandbox(path)
    assert result.ok
    os.unlink(path)


def test_sandbox_catches_exceptions():
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py") as f:
        f.write("raise ValueError('boom')\n")
        f.flush()
        path = f.name

    result = run_in_sandbox(path)
    assert not result.ok
    assert "ValueError" in result.error
    os.unlink(path)
