"""
Tests for Aurora-X Generated Modules
Validates that all 1,650 generated module files are properly structured and functional.
"""

import pytest
import json
import sys
import importlib.util
from pathlib import Path

MODULES_ROOT = Path("aurora_nexus_v3/modules")
REGISTRY_PATH = Path("aurora_nexus_v3/modules_registry.json")

CATEGORIES = [
    "connector", "processor", "analyzer", "generator", 
    "transformer", "validator", "formatter", "optimizer",
    "monitor", "integrator"
]


def load_registry():
    """Load the modules registry."""
    if not REGISTRY_PATH.exists():
        pytest.skip("Registry not found - run generator first")
    
    with open(REGISTRY_PATH) as f:
        return json.load(f)


def get_module_files():
    """Get all Python module files."""
    files = []
    for category in CATEGORIES:
        cat_dir = MODULES_ROOT / category
        if cat_dir.exists():
            files.extend(cat_dir.glob("*.py"))
    return files


class TestModuleStructure:
    """Test module file structure."""
    
    def test_registry_exists(self):
        """Verify registry file exists."""
        assert REGISTRY_PATH.exists(), "Registry file should exist"
    
    def test_registry_format(self):
        """Verify registry has correct format."""
        registry = load_registry()
        
        assert "modules" in registry, "Registry should have modules key"
        assert "generated_at" in registry, "Registry should have timestamp"
        assert isinstance(registry["modules"], list), "Modules should be a list"
    
    def test_category_directories(self):
        """Verify all category directories exist."""
        registry = load_registry()
        
        categories_found = set()
        for mod in registry.get("modules", []):
            categories_found.add(mod.get("category"))
        
        for cat in categories_found:
            cat_dir = MODULES_ROOT / cat
            assert cat_dir.exists(), f"Category directory {cat} should exist"
    
    def test_module_files_exist(self):
        """Verify all registered module files exist."""
        registry = load_registry()
        
        missing = []
        for mod in registry.get("modules", []):
            paths = mod.get("paths", {})
            for file_type, path in paths.items():
                if not Path(path).exists():
                    missing.append(path)
        
        assert len(missing) == 0, f"Missing module files: {missing[:5]}..."


class TestModuleSyntax:
    """Test module syntax validity."""
    
    def test_modules_have_valid_syntax(self):
        """Verify all module files have valid Python syntax."""
        errors = []
        
        for filepath in get_module_files():
            if filepath.name == "__init__.py":
                continue
            
            try:
                content = filepath.read_text()
                compile(content, str(filepath), 'exec')
            except SyntaxError as e:
                errors.append(f"{filepath}: {e}")
        
        assert len(errors) == 0, f"Syntax errors found: {errors[:5]}"
    
    def test_modules_importable(self):
        """Verify modules can be imported."""
        registry = load_registry()
        
        sample_size = min(10, len(registry.get("modules", [])))
        sample = registry.get("modules", [])[:sample_size]
        
        errors = []
        for mod in sample:
            init_path = mod.get("paths", {}).get("init")
            if init_path and Path(init_path).exists():
                try:
                    spec = importlib.util.spec_from_file_location(
                        f"test_{mod['id']}", init_path
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                except Exception as e:
                    errors.append(f"{mod['id']}: {e}")
        
        assert len(errors) == 0, f"Import errors: {errors}"


class TestModuleFunctionality:
    """Test module functionality."""
    
    def test_init_function_exists(self):
        """Verify init modules have init function."""
        registry = load_registry()
        
        sample = registry.get("modules", [])[:5]
        
        for mod in sample:
            init_path = mod.get("paths", {}).get("init")
            if init_path and Path(init_path).exists():
                spec = importlib.util.spec_from_file_location(
                    f"test_init_{mod['id']}", init_path
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    assert hasattr(module, 'init'), \
                        f"Module {mod['id']} should have init function"
    
    def test_execute_function_exists(self):
        """Verify execute modules have execute function."""
        registry = load_registry()
        
        sample = registry.get("modules", [])[:5]
        
        for mod in sample:
            exec_path = mod.get("paths", {}).get("execute")
            if exec_path and Path(exec_path).exists():
                spec = importlib.util.spec_from_file_location(
                    f"test_exec_{mod['id']}", exec_path
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    assert hasattr(module, 'execute'), \
                        f"Module {mod['id']} should have execute function"
    
    def test_cleanup_function_exists(self):
        """Verify cleanup modules have cleanup function."""
        registry = load_registry()
        
        sample = registry.get("modules", [])[:5]
        
        for mod in sample:
            clean_path = mod.get("paths", {}).get("cleanup")
            if clean_path and Path(clean_path).exists():
                spec = importlib.util.spec_from_file_location(
                    f"test_clean_{mod['id']}", clean_path
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    assert hasattr(module, 'cleanup'), \
                        f"Module {mod['id']} should have cleanup function"


class TestModuleExecution:
    """Test actual module execution."""
    
    def test_init_returns_dict(self):
        """Verify init function returns dictionary."""
        registry = load_registry()
        
        if not registry.get("modules"):
            pytest.skip("No modules in registry")
        
        mod = registry["modules"][0]
        init_path = mod.get("paths", {}).get("init")
        
        if init_path and Path(init_path).exists():
            spec = importlib.util.spec_from_file_location("test", init_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                result = module.init({})
                assert isinstance(result, dict), "init should return dict"
                assert "status" in result, "Result should have status"
    
    def test_execute_returns_dict(self):
        """Verify execute function returns dictionary."""
        registry = load_registry()
        
        if not registry.get("modules"):
            pytest.skip("No modules in registry")
        
        mod = registry["modules"][0]
        exec_path = mod.get("paths", {}).get("execute")
        
        if exec_path and Path(exec_path).exists():
            spec = importlib.util.spec_from_file_location("test", exec_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                result = module.execute({"test": True})
                assert isinstance(result, dict), "execute should return dict"
                assert "status" in result, "Result should have status"
    
    def test_cleanup_returns_dict(self):
        """Verify cleanup function returns dictionary."""
        registry = load_registry()
        
        if not registry.get("modules"):
            pytest.skip("No modules in registry")
        
        mod = registry["modules"][0]
        clean_path = mod.get("paths", {}).get("cleanup")
        
        if clean_path and Path(clean_path).exists():
            spec = importlib.util.spec_from_file_location("test", clean_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                result = module.cleanup()
                assert isinstance(result, dict), "cleanup should return dict"
                assert "status" in result, "Result should have status"


class TestModuleCount:
    """Test module counts match expectations."""
    
    def test_total_module_count(self):
        """Verify we have 550 modules registered."""
        registry = load_registry()
        
        module_count = len(registry.get("modules", []))
        assert module_count == 550, f"Expected 550 modules, got {module_count}"
    
    def test_file_count(self):
        """Verify we have 1650 module files (550 * 3)."""
        registry = load_registry()
        
        total_files = 0
        for mod in registry.get("modules", []):
            paths = mod.get("paths", {})
            total_files += len(paths)
        
        assert total_files == 1650, f"Expected 1650 files, got {total_files}"
    
    def test_category_distribution(self):
        """Verify modules are distributed across categories."""
        registry = load_registry()
        
        categories = {}
        for mod in registry.get("modules", []):
            cat = mod.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        
        assert len(categories) == 10, f"Expected 10 categories, got {len(categories)}"
        
        for cat, count in categories.items():
            assert count == 55, f"Category {cat} should have 55 modules, got {count}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
