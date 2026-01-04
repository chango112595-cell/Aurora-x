"""
Module Integrity Test Suite
Validates that every generated module has the proper lifecycle hooks.
"""

import importlib
import importlib.util
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MODULE_PATH = pathlib.Path("aurora_x/core/modules")


def test_modules_directory_exists():
    """Verify modules directory exists."""
    assert MODULE_PATH.exists(), f"Modules directory not found at {MODULE_PATH}"
    assert MODULE_PATH.is_dir(), f"{MODULE_PATH} is not a directory"


def test_all_modules_present():
    """Verify all 550 modules are present."""
    files = list(MODULE_PATH.glob("module_*.py"))
    assert len(files) == 550, f"Expected 550 modules, found {len(files)}"


def test_module_manifest_exists():
    """Verify modules manifest exists and is valid JSON."""
    import json

    manifest_path = MODULE_PATH / "modules.manifest.json"
    assert manifest_path.exists(), f"Manifest not found at {manifest_path}"

    with open(manifest_path) as f:
        data = json.load(f)

    assert "modules" in data, "Manifest should contain 'modules' key"
    assert len(data["modules"]) == 550, (
        f"Manifest should list 550 modules, found {len(data['modules'])}"
    )


def test_sample_modules_structure():
    """Test a sample of modules for proper structure."""
    sample_ids = [1, 50, 100, 250, 400, 550]

    for module_id in sample_ids:
        module_file = MODULE_PATH / f"module_{module_id:03d}.py"
        assert module_file.exists(), f"Module {module_id} not found"

        spec = importlib.util.spec_from_file_location(f"module_{module_id:03d}", module_file)
        assert spec is not None, f"Failed to load spec for module {module_id}"
        assert spec.loader is not None, f"No loader for module {module_id}"

        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        class_name = f"AuroraModule{module_id:03d}"
        assert hasattr(mod, class_name), f"Module {module_id} missing class {class_name}"

        cls = getattr(mod, class_name)
        instance = cls()

        required_methods = ["execute", "on_boot", "on_tick", "on_reflect"]
        for method in required_methods:
            assert hasattr(instance, method), f"Module {module_id} missing {method}"
            assert callable(getattr(instance, method)), (
                f"{method} is not callable in module {module_id}"
            )


def test_required_functions_exist():
    """Verify all modules have required lifecycle hooks."""
    errors = []

    for i in range(1, 551):
        module_file = MODULE_PATH / f"module_{i:03d}.py"

        if not module_file.exists():
            errors.append(f"module_{i:03d}.py missing")
            continue

        try:
            spec = importlib.util.spec_from_file_location(f"module_{i:03d}", module_file)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            class_name = f"AuroraModule{i:03d}"
            if not hasattr(mod, class_name):
                errors.append(f"module_{i:03d} missing class {class_name}")
                continue

            cls = getattr(mod, class_name)
            instance = cls()

            for fn in ["execute", "on_boot", "on_tick", "on_reflect"]:
                if not hasattr(instance, fn):
                    errors.append(f"module_{i:03d} missing {fn}")
        except Exception as e:
            errors.append(f"module_{i:03d} error: {str(e)}")

    assert len(errors) == 0, "Module integrity errors:\n" + "\n".join(errors[:20])


def test_module_metadata():
    """Verify modules have required metadata attributes."""
    sample_ids = [1, 100, 300, 550]

    for module_id in sample_ids:
        module_file = MODULE_PATH / f"module_{module_id:03d}.py"

        spec = importlib.util.spec_from_file_location(f"module_{module_id:03d}", module_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        class_name = f"AuroraModule{module_id:03d}"
        cls = getattr(mod, class_name)
        instance = cls()

        assert hasattr(instance, "module_id"), f"Module {module_id} missing module_id"
        assert hasattr(instance, "name"), f"Module {module_id} missing name"
        assert hasattr(instance, "category"), f"Module {module_id} missing category"
        assert hasattr(instance, "temporal_tier"), f"Module {module_id} missing temporal_tier"


def test_module_execution_returns_dict():
    """Verify module execution returns proper dictionary structure."""
    sample_ids = [1, 50, 250, 550]

    for module_id in sample_ids:
        module_file = MODULE_PATH / f"module_{module_id:03d}.py"

        spec = importlib.util.spec_from_file_location(f"module_{module_id:03d}", module_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        class_name = f"AuroraModule{module_id:03d}"
        cls = getattr(mod, class_name)
        instance = cls()

        result = instance.execute({"task": "test"})

        assert isinstance(result, dict), f"Module {module_id} execute() should return dict"
        assert "status" in result, f"Module {module_id} result missing 'status'"
        assert "module" in result, f"Module {module_id} result missing 'module'"
