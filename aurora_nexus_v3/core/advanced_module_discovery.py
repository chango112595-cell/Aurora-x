"""
Advanced Module Discovery System
Self-contained intelligent module discovery with dependency analysis and integration
No external APIs - uses AST parsing, dependency graphs, and pattern matching
"""

import ast
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from .advanced_reasoning_engine import AdvancedReasoningEngine


class ModuleType(Enum):
    """Module types"""

    CORE = "core"
    UTILITY = "utility"
    WORKER = "worker"
    INTEGRATION = "integration"
    ADAPTER = "adapter"
    SERVICE = "service"


@dataclass
class DiscoveredModule:
    """A discovered module"""

    module_id: str
    module_path: str
    module_name: str
    module_type: ModuleType
    dependencies: list[str]
    exports: list[str]
    imports: list[str]
    functions: list[str]
    classes: list[str]
    complexity_score: float
    discovered_at: datetime = field(default_factory=datetime.now)


class AdvancedModuleDiscovery:
    """
    Self-contained advanced module discovery system
    Intelligently discovers and analyzes modules
    """

    def __init__(self, codebase_root: str = "."):
        self.codebase_root = Path(codebase_root)
        self.reasoning_engine = AdvancedReasoningEngine()
        self.discovered_modules: dict[str, DiscoveredModule] = {}
        self.module_graph: dict[str, list[str]] = {}  # module -> [dependencies]
        self.discovery_patterns: dict[str, list[str]] = {}
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize discovery patterns"""
        self.discovery_patterns = {
            "core": ["core", "engine", "system"],
            "utility": ["util", "helper", "tool"],
            "worker": ["worker", "executor", "handler"],
            "integration": ["integration", "bridge", "adapter"],
        }

    def discover_modules(self, directory: str | None = None) -> list[DiscoveredModule]:
        """Discover all modules in codebase"""
        search_path = Path(directory) if directory else self.codebase_root

        discovered = []

        # Find all Python files
        for py_file in search_path.rglob("*.py"):
            if self._should_scan_file(py_file):
                module = self._analyze_module(py_file)
                if module:
                    self.discovered_modules[module.module_id] = module
                    discovered.append(module)

        # Build dependency graph
        self._build_dependency_graph()

        return discovered

    def _should_scan_file(self, file_path: Path) -> bool:
        """Determine if file should be scanned"""
        # Skip test files, migrations, etc.
        skip_patterns = [
            "__pycache__",
            ".pyc",
            "test_",
            "_test.py",
            "migrations",
            "venv",
            ".venv",
        ]

        path_str = str(file_path)
        return not any(pattern in path_str for pattern in skip_patterns)

    def _analyze_module(self, file_path: Path) -> DiscoveredModule | None:
        """Analyze a module file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                code = f.read()

            # Parse AST
            tree = ast.parse(code)

            # Extract information
            module_name = file_path.stem
            module_type = self._classify_module_type(file_path, code)
            dependencies = self._extract_dependencies(tree)
            exports = self._extract_exports(tree)
            imports = self._extract_imports(tree)
            functions = self._extract_functions(tree)
            classes = self._extract_classes(tree)
            complexity_score = self._calculate_complexity(tree)

            module = DiscoveredModule(
                module_id=str(uuid.uuid4()),
                module_path=str(file_path),
                module_name=module_name,
                module_type=module_type,
                dependencies=dependencies,
                exports=exports,
                imports=imports,
                functions=functions,
                classes=classes,
                complexity_score=complexity_score,
            )

            return module

        except Exception:
            return None

    def _classify_module_type(self, file_path: Path, code: str) -> ModuleType:
        """Classify module type"""
        path_str = str(file_path).lower()
        code_lower = code.lower()

        # Check path patterns
        for module_type, patterns in self.discovery_patterns.items():
            if any(pattern in path_str for pattern in patterns):
                return ModuleType(module_type)

        # Check code patterns
        if "class" in code_lower and "worker" in code_lower:
            return ModuleType.WORKER
        elif "class" in code_lower and "adapter" in code_lower:
            return ModuleType.ADAPTER
        elif "def" in code_lower and "integrate" in code_lower:
            return ModuleType.INTEGRATION

        return ModuleType.UTILITY  # Default

    def _extract_dependencies(self, tree: ast.AST) -> list[str]:
        """Extract module dependencies"""
        dependencies = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.append(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                dependencies.append(node.module.split(".")[0])

        return list(set(dependencies))

    def _extract_exports(self, tree: ast.AST) -> list[str]:
        """Extract exported symbols"""
        exports = []

        # Check for __all__
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, ast.List):
                            exports.extend(
                                elt.s for elt in node.value.elts if isinstance(elt, ast.Str)
                            )

        return exports

    def _extract_imports(self, tree: ast.AST) -> list[str]:
        """Extract imports"""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)

        return list(set(imports))

    def _extract_functions(self, tree: ast.AST) -> list[str]:
        """Extract function names"""
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)

        return functions

    def _extract_classes(self, tree: ast.AST) -> list[str]:
        """Extract class names"""
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)

        return classes

    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calculate module complexity"""
        complexity = 0.0

        # Count functions and classes
        function_count = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
        class_count = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])

        # Count control flow complexity
        control_flow_nodes = [
            ast.If,
            ast.For,
            ast.While,
            ast.Try,
            ast.With,
        ]
        control_flow_count = sum(
            1 for n in ast.walk(tree) if isinstance(n, tuple(control_flow_nodes))
        )

        # Calculate complexity score
        complexity = (function_count * 0.1) + (class_count * 0.2) + (control_flow_count * 0.05)

        return min(complexity, 10.0)  # Cap at 10

    def _build_dependency_graph(self):
        """Build dependency graph"""
        self.module_graph = {}

        for module_id, module in self.discovered_modules.items():
            self.module_graph[module_id] = module.dependencies

    def find_module_by_name(self, name: str) -> DiscoveredModule | None:
        """Find module by name"""
        for module in self.discovered_modules.values():
            if module.module_name == name or name in module.module_path:
                return module
        return None

    def get_module_dependencies(self, module_id: str) -> list[str]:
        """Get dependencies of a module"""
        return self.module_graph.get(module_id, [])

    def get_discovery_stats(self) -> dict[str, Any]:
        """Get discovery statistics"""
        return {
            "total_modules": len(self.discovered_modules),
            "modules_by_type": {
                mt.value: len([m for m in self.discovered_modules.values() if m.module_type == mt])
                for mt in ModuleType
            },
            "average_complexity": (
                sum(m.complexity_score for m in self.discovered_modules.values())
                / len(self.discovered_modules)
                if self.discovered_modules
                else 0.0
            ),
            "total_dependencies": sum(
                len(m.dependencies) for m in self.discovered_modules.values()
            ),
        }
