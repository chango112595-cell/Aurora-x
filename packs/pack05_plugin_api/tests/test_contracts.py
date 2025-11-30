#!/usr/bin/env python3
import tempfile
import os
import yaml
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.contracts import (
    validate_manifest,
    validate_api,
    ContractViolation
)


def test_manifest_validation_success():
    manifest = {
        "name": "demo",
        "version": "1.0.0",
        "entrypoint": "plugin.py",
        "api_level": 1,
    }

    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".yaml") as f:
        yaml.dump(manifest, f)
        f.flush()
        path = f.name

    assert validate_manifest(path) == True
    os.unlink(path)


def test_manifest_validation_failure():
    bad_manifest = {
        "name": "broken"
    }

    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".yaml") as f:
        yaml.dump(bad_manifest, f)
        f.flush()
        path = f.name

    try:
        validate_manifest(path)
        assert False, "Should have raised"
    except ContractViolation:
        pass
    os.unlink(path)


def test_runtime_api_checks():
    class Example:
        def start(self): pass
        def stop(self): pass

    validate_api(Example(), ["start", "stop"])


def test_runtime_api_missing_methods():
    class Example:
        def start(self): pass

    try:
        validate_api(Example(), ["start", "stop"])
        assert False
    except ContractViolation:
        pass
