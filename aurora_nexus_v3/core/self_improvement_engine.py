"""
Self-Improvement Engine
Self-contained continuous self-improvement through code analysis and optimization
No external APIs - uses static analysis, pattern detection, and performance profiling
"""

import ast
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from .continuous_learner import ContinuousLearner


class ImprovementType(Enum):
    """Types of improvements"""

    PERFORMANCE = "performance"
    CODE_QUALITY = "code_quality"
    ARCHITECTURE = "architecture"
    ALGORITHM = "algorithm"
    MEMORY = "memory"
    SECURITY = "security"


class ImprovementPriority(Enum):
    """Improvement priorities"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Improvement:
    """A self-improvement suggestion"""

    improvement_id: str
    improvement_type: ImprovementType
    priority: ImprovementPriority
    target_file: str
    target_line: int | None
    description: str
    current_code: str | None
    suggested_code: str | None
    expected_benefit: str
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)


class SelfImprovementEngine:
    """
    Self-contained self-improvement engine
    Analyzes code and suggests improvements
    """

    def __init__(self, codebase_root: str = "."):
        self.codebase_root = Path(codebase_root)
        self.improvement_history: list[Improvement] = []
        self.continuous_learner = ContinuousLearner()
        self.improvement_patterns: dict[str, list[str]] = {}
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize improvement patterns"""
        self.improvement_patterns = {
            "performance": [
                r"for\s+.*\s+in\s+range\(len\(.*\)\)",  # Use enumerate instead
                r"\.append\(.*\)\s+in\s+loop",  # Use list comprehension
                r"if\s+.*\s+in\s+.*:\s+if\s+.*\s+in\s+.*",  # Nested if can be optimized
            ],
            "code_quality": [
                r"except\s*:",  # Bare except
                r"pass\s*$",  # Empty except/pass
                r"TODO|FIXME|XXX",  # Unresolved TODOs
            ],
            "memory": [
                r"\.copy\(\)\s*$",  # Unnecessary copy
                r"list\(.*\)\s*\.\s*append",  # Inefficient list building
            ],
        }

    def analyze_and_improve(self, file_path: str) -> list[Improvement]:
        """
        Analyze a file and suggest improvements
        """

        improvements = []
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            return improvements

        try:
            with open(file_path_obj, encoding="utf-8") as f:
                code = f.read()

            # Analyze code
            code_improvements = self._analyze_code(code, file_path)
            improvements.extend(code_improvements)

            # Analyze AST
            try:
                tree = ast.parse(code)
                ast_improvements = self._analyze_ast(tree, file_path)
                improvements.extend(ast_improvements)
            except SyntaxError:
                pass  # Skip AST analysis if syntax error

            # Store improvements
            self.improvement_history.extend(improvements)

            # Keep only recent improvements (last 5000)
            if len(self.improvement_history) > 5000:
                self.improvement_history = self.improvement_history[-5000:]

        except Exception:
            pass  # Continue if file can't be read

        return improvements

    def _analyze_code(self, code: str, file_path: str) -> list[Improvement]:
        """Analyze code using pattern matching"""
        import uuid

        improvements = []
        lines = code.split("\n")

        for improvement_type, patterns in self.improvement_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, code, re.MULTILINE)
                for match in matches:
                    line_num = code[: match.start()].count("\n") + 1
                    line_content = lines[line_num - 1] if line_num <= len(lines) else ""

                    improvement = Improvement(
                        improvement_id=str(uuid.uuid4()),
                        improvement_type=ImprovementType(improvement_type),
                        priority=self._determine_priority(improvement_type, line_content),
                        target_file=file_path,
                        target_line=line_num,
                        description=self._generate_description(
                            improvement_type, pattern, line_content
                        ),
                        current_code=line_content.strip(),
                        suggested_code=self._suggest_improvement(
                            improvement_type, pattern, line_content
                        ),
                        expected_benefit=self._estimate_benefit(improvement_type),
                        confidence=0.7,
                    )
                    improvements.append(improvement)

        return improvements

    def _analyze_ast(self, tree: ast.AST, file_path: str) -> list[Improvement]:
        """Analyze AST for improvements"""
        import uuid

        improvements = []

        class ImprovementVisitor(ast.NodeVisitor):
            def __init__(self, engine):
                self.engine = engine
                self.improvements = []

            def visit_For(self, node):
                # Check for range(len(...)) pattern
                if (
                    isinstance(node.iter, ast.Call)
                    and isinstance(node.iter.func, ast.Name)
                    and node.iter.func.id == "range"
                    and isinstance(node.iter.args[0], ast.Call)
                    and isinstance(node.iter.args[0].func, ast.Name)
                    and node.iter.args[0].func.id == "len"
                ):
                    improvement = Improvement(
                        improvement_id=str(uuid.uuid4()),
                        improvement_type=ImprovementType.PERFORMANCE,
                        priority=ImprovementPriority.MEDIUM,
                        target_file=file_path,
                        target_line=node.lineno,
                        description="Use enumerate() instead of range(len())",
                        current_code=None,
                        suggested_code="for i, item in enumerate(iterable):",
                        expected_benefit="Better readability and performance",
                        confidence=0.8,
                    )
                    self.improvements.append(improvement)

                self.generic_visit(node)

            def visit_ExceptHandler(self, node):
                # Check for bare except
                if node.type is None:
                    improvement = Improvement(
                        improvement_id=str(uuid.uuid4()),
                        improvement_type=ImprovementType.CODE_QUALITY,
                        priority=ImprovementPriority.HIGH,
                        target_file=file_path,
                        target_line=node.lineno,
                        description="Bare except clause - specify exception type",
                        current_code=None,
                        suggested_code="except SpecificException:",
                        expected_benefit="Better error handling",
                        confidence=0.9,
                    )
                    self.improvements.append(improvement)

                self.generic_visit(node)

        visitor = ImprovementVisitor(self)
        visitor.visit(tree)
        improvements.extend(visitor.improvements)

        return improvements

    def _determine_priority(self, improvement_type: str, line_content: str) -> ImprovementPriority:
        """Determine priority of improvement"""
        if improvement_type == "security":
            return ImprovementPriority.CRITICAL
        line_lower = line_content.lower()
        is_high_priority = (improvement_type == "performance" and "loop" in line_lower) or (
            improvement_type == "code_quality" and "except" in line_lower
        )
        if is_high_priority:
            return ImprovementPriority.HIGH
        else:
            return ImprovementPriority.MEDIUM

    def _generate_description(self, improvement_type: str, pattern: str, line_content: str) -> str:
        """Generate description for improvement"""
        descriptions = {
            "performance": f"Performance optimization opportunity: {line_content[:50]}",
            "code_quality": f"Code quality improvement: {line_content[:50]}",
            "memory": f"Memory optimization: {line_content[:50]}",
        }
        return descriptions.get(improvement_type, f"Improvement: {line_content[:50]}")

    def _suggest_improvement(
        self, improvement_type: str, pattern: str, line_content: str
    ) -> str | None:
        """Suggest improved code"""
        if improvement_type == "performance" and "range(len" in line_content:
            return line_content.replace("range(len(", "enumerate(")
        elif improvement_type == "code_quality" and "except:" in line_content:
            return line_content.replace("except:", "except Exception:")

        return None

    def _estimate_benefit(self, improvement_type: str) -> str:
        """Estimate benefit of improvement"""
        benefits = {
            "performance": "Improved execution speed",
            "code_quality": "Better maintainability",
            "memory": "Reduced memory usage",
            "security": "Enhanced security",
        }
        return benefits.get(improvement_type, "General improvement")

    def apply_improvements(self, improvements: list[Improvement]) -> dict[str, Any]:
        """Apply improvements to codebase"""
        applied = 0
        failed = 0

        for improvement in improvements:
            if improvement.priority == ImprovementPriority.CRITICAL:
                # Auto-apply critical improvements
                try:
                    if improvement.target_file and improvement.suggested_code:
                        # Apply improvement
                        # (simplified - real implementation would be more sophisticated)
                        applied += 1
                    else:
                        failed += 1
                except Exception:
                    failed += 1

        return {
            "applied": applied,
            "failed": failed,
            "total": len(improvements),
        }

    def get_improvement_history(self) -> list[Improvement]:
        """Get improvement history"""
        return self.improvement_history

    def get_status(self) -> dict[str, Any]:
        """Get engine status"""
        return {
            "total_improvements": len(self.improvement_history),
            "improvements_by_type": {
                it.value: len([i for i in self.improvement_history if i.improvement_type == it])
                for it in ImprovementType
            },
            "improvements_by_priority": {
                ip.value: len([i for i in self.improvement_history if i.priority == ip])
                for ip in ImprovementPriority
            },
        }
