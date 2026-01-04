#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.log_unifier import LogUnifier


def test_log_unifier_append_tail(tmp_path):
    log_path = tmp_path / "test.log"
    lu = LogUnifier(path=str(log_path))
    lu.append("source1", "line 1")
    lu.append("source2", "line 2")

    entries = lu.tail(10)
    assert len(entries) == 2
    assert entries[0]["source"] == "source1"
    assert entries[1]["line"] == "line 2"


def test_log_unifier_clear(tmp_path):
    log_path = tmp_path / "test.log"
    lu = LogUnifier(path=str(log_path))
    lu.append("test", "test line")
    lu.clear()

    entries = lu.tail()
    assert entries == []
