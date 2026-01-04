#!/usr/bin/env python3
import time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eventbus import EventBus

def test_eventbus_publish_poll():
    b = EventBus()
    b.publish("test.topic", {"x":1})
    ev = b.poll(timeout=0.2)
    assert ev is not None
    assert ev["topic"] == "test.topic"
    assert ev["data"] == {"x":1}
