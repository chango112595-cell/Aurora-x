"""
Code Quality Intelligence System
Self-contained deep code quality analysis with smell detection and best practices
No external APIs - uses AST analysis, pattern recognition, and quality metrics
"""

import ast
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any


class QualityLevel(Enum):
    """Code quality level"""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class CodeSmell:
    """Code smell"""

    type: str
    severity: str
    location: str
    description: str
    recommendation: str


@dataclass
class QualityMetrics:
    """Code quality metrics"""

    complexity: float
    maintainability_index: float
    code_smells: int
    test_coverage: float
    documentation_coverage: float
    overall_quality: QualityLevel


class CodeQualityIntelligence:
    """
    Self-contained code quality intelligence system
    Deep code quality analysis with smell detection and best practices
    """

    def __init__(self):
        self.smell_patterns = {
            "long_method": {
                "threshold": 50,
                "description": "Method exceeds recommended line count",
            },
            "long_parameter_list": {"threshold": 5, "description": "Too many parameters"},
            "duplicate_code": {"description": "Code duplication detected"},
            "god_class": {"threshold": 500, "description": "Class with too many responsibilities"},
            "feature_envy": {"description": "Method accesses data from another class excessively"},
            "data_clumps": {"description": "Groups of data that should be objects"},
            "primitive_obsession": {"description": "Overuse of primitive types"},
            "long_chain": {"threshold": 5, "description": "Long method call chain"},
        }

    def analyze_code_quality(self, code: str, file_path: str = "") -> dict[str, Any]:
        """Analyze code quality"""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {
                "valid": False,
                "error": "Invalid syntax",
                "quality_level": QualityLevel.CRITICAL.value,
            }

        # Calculate metrics
        complexity = self._calculate_complexity(tree)
        maintainability = self._calculate_maintainability_index(code, complexity)
        smells = self._detect_code_smells(code, tree, file_path)
        doc_coverage = self._calculate_documentation_coverage(code, tree)

        # Determine overall quality
        quality_score = maintainability * 0.4 + (100 - len(smells) * 10) * 0.3 + doc_coverage * 0.3
        quality_score = max(0, min(100, quality_score))

        if quality_score >= 80:
            quality_level = QualityLevel.EXCELLENT
        elif quality_score >= 60:
            quality_level = QualityLevel.GOOD
        elif quality_score >= 40:
            quality_level = QualityLevel.FAIR
        elif quality_score >= 20:
            quality_level = QualityLevel.POOR
        else:
            quality_level = QualityLevel.CRITICAL

        quality_metrics = QualityMetrics(
            complexity=complexity,
            maintainability_index=maintainability,
            code_smells=len(smells),
            test_coverage=0.0,  # Would need test analysis
            documentation_coverage=doc_coverage,
            overall_quality=quality_level,
        )

        return {
            "valid": True,
            "quality_metrics": quality_metrics,
            "metrics": {
                "complexity": complexity,
                "maintainability_index": maintainability,
                "code_smells": len(smells),
                "documentation_coverage": doc_coverage,
                "quality_score": quality_score,
                "quality_level": quality_level.value,
            },
            "smells": [
                {
                    "type": smell.type,
                    "severity": smell.severity,
                    "location": smell.location,
                    "description": smell.description,
                    "recommendation": smell.recommendation,
                }
                for smell in smells
            ],
        }

    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity

    def _calculate_maintainability_index(self, code: str, complexity: float) -> float:
        """Calculate maintainability index (simplified)"""
        lines = len(code.split("\n"))
        avg_line_length = sum(len(line) for line in code.split("\n")) / max(lines, 1)

        # Simplified maintainability index
        # Lower complexity, fewer lines, shorter lines = higher maintainability
        maintainability = 100.0
        maintainability -= min(complexity * 2, 40)  # Complexity penalty
        maintainability -= min(lines / 10, 30)  # Size penalty
        maintainability -= min(avg_line_length / 2, 30)  # Length penalty

        return max(0, min(100, maintainability))

    def _detect_code_smells(self, code: str, tree: ast.AST, file_path: str) -> list[CodeSmell]:
        """Detect code smells"""
        smells: list[CodeSmell] = []

        # Check for long methods
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = node.end_lineno - node.lineno if hasattr(node, "end_lineno") else 0
                if func_lines > self.smell_patterns["long_method"]["threshold"]:
                    smells.append(
                        CodeSmell(
                            type="long_method",
                            severity="medium",
                            location=f"{file_path}:{node.lineno}",
                            description=f"Method '{node.name}' has {func_lines} lines",
                            recommendation="Break down into smaller methods",
                        )
                    )

                # Check parameter count
                param_count = len(node.args.args)
                if param_count > self.smell_patterns["long_parameter_list"]["threshold"]:
                    smells.append(
                        CodeSmell(
                            type="long_parameter_list",
                            severity="medium",
                            location=f"{file_path}:{node.lineno}",
                            description=f"Method '{node.name}' has {param_count} parameters",
                            recommendation="Use parameter objects or builder pattern",
                        )
                    )

        # Check for duplicate code (simplified - check for repeated patterns)
        lines = code.split("\n")
        line_patterns: dict[str, int] = {}
        for line in lines:
            stripped = line.strip()
            if len(stripped) > 20:  # Only check substantial lines
                line_patterns[stripped] = line_patterns.get(stripped, 0) + 1

        duplicate_lines = [line for line, count in line_patterns.items() if count > 3]
        if duplicate_lines:
            smells.append(
                CodeSmell(
                    type="duplicate_code",
                    severity="low",
                    location=file_path,
                    description=f"Found {len(duplicate_lines)} duplicate line patterns",
                    recommendation="Extract common code into reusable functions",
                )
            )

        # Check for long chains
        chain_pattern = r"\w+\.\w+(\.\w+){4,}"
        matches = re.finditer(chain_pattern, code)
        for match in matches:
            line_num = code[: match.start()].count("\n") + 1
            smells.append(
                CodeSmell(
                    type="long_chain",
                    severity="low",
                    location=f"{file_path}:{line_num}",
                    description="Long method call chain detected",
                    recommendation="Use intermediate variables or extract methods",
                )
            )

        return smells

    def _calculate_documentation_coverage(self, code: str, tree: ast.AST) -> float:
        """Calculate documentation coverage"""
        total_functions = 0
        documented_functions = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_functions += 1
                if ast.get_docstring(node):
                    documented_functions += 1

        if total_functions == 0:
            return 100.0

        return (documented_functions / total_functions) * 100

    def detect_performance_anti_patterns(self, code: str) -> list[dict[str, Any]]:
        """Detect performance anti-patterns"""
        anti_patterns: list[dict[str, Any]] = []

        # Check for nested loops
        nested_loop_pattern = r"for\s+.*:\s*\n.*for\s+.*:"
        if re.search(nested_loop_pattern, code, re.MULTILINE):
            anti_patterns.append(
                {
                    "pattern": "nested_loops",
                    "severity": "medium",
                    "description": "Nested loops detected - consider optimization",
                    "recommendation": "Use vectorized operations or optimize algorithm",
                }
            )

        # Check for string concatenation in loops
        loop_concat_pattern = r"for\s+.*:\s*\n.*\+\s*="
        if re.search(loop_concat_pattern, code, re.MULTILINE):
            anti_patterns.append(
                {
                    "pattern": "string_concatenation_in_loop",
                    "severity": "low",
                    "description": "String concatenation in loop",
                    "recommendation": "Use list.join() or string builder",
                }
            )

        # Check for unnecessary list copies
        list_copy_pattern = r"list\(\[.*\]\)|\[.*\]\.copy\(\)"
        if re.search(list_copy_pattern, code):
            anti_patterns.append(
                {
                    "pattern": "unnecessary_copy",
                    "severity": "low",
                    "description": "Unnecessary list copy detected",
                    "recommendation": "Use direct reference or slice if needed",
                }
            )

        return anti_patterns

    def enforce_best_practices(self, code: str) -> dict[str, Any]:
        """Enforce best practices"""
        recommendations: list[str] = []
        violations: list[dict[str, Any]] = []

        # Check for proper error handling
        if "try:" in code and "except" not in code:
            recommendations.append("Add exception handling for try blocks")
            violations.append({"type": "missing_exception_handling", "severity": "high"})

        # Check for type hints (Python)
        if "def " in code and "->" not in code:
            recommendations.append("Consider adding type hints to function signatures")
            violations.append({"type": "missing_type_hints", "severity": "low"})

        # Check for magic numbers
        magic_number_pattern = r"\b\d{3,}\b"
        matches = re.finditer(magic_number_pattern, code)
        magic_numbers = [m.group(0) for m in matches]
        if magic_numbers:
            recommendations.append("Replace magic numbers with named constants")
            violations.append({"type": "magic_numbers", "severity": "low"})

        return {
            "recommendations": recommendations,
            "violations": violations,
            "compliance_score": max(0, 100 - len(violations) * 10),
        }
