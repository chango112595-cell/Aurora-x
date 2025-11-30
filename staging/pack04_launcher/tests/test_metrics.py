#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.metrics import Metrics

def test_metrics_record(tmp_path):
    metrics_path = tmp_path / "metrics.json"
    m = Metrics(path=str(metrics_path))
    m.record("job1", 0)
    m.record("job1", 1)
    m.record("job2", 0)
    
    assert m.last_rc("job1") == 1
    assert m.last_rc("job2") == 0
    assert m.last_rc("nonexistent") is None

def test_metrics_all_records(tmp_path):
    metrics_path = tmp_path / "metrics.json"
    m = Metrics(path=str(metrics_path))
    m.record("test", 0)
    m.record("test", 1)
    
    records = m.all_records()
    assert len(records) == 2
