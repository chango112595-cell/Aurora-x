"""
Self-Verification System
Self-contained comprehensive self-verification with code correctness and solution validation
No external APIs - uses static analysis, pattern matching, and safety checks
"""

import ast
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any


class VerificationResult(Enum):
    """Verification result"""

    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


@dataclass
class VerificationIssue:
    """Verification issue"""

    result: VerificationResult
    category: str
    message: str
    location: str | None = None
    code_snippet: str | None = None


class SelfVerificationSystem:
    """
    Self-contained self-verification system
    Comprehensive verification with code correctness and solution validation
    """

    def __init__(self):
        self.verification_history: list[VerificationIssue] = []

    def verify_code_correctness(self, code: str, file_path: str = "") -> list[VerificationIssue]:
        """Verify code correctness"""
        issues: list[VerificationIssue] = []

        # Syntax check
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append(
                VerificationIssue(
                    result=VerificationResult.FAIL,
                    category="syntax",
                    message=f"Syntax error: {e.msg}",
                    location=f"{file_path}:{e.lineno}",
                )
            )
            return issues  # Can't continue if syntax is invalid

        # Check for common errors
        issues.extend(self._check_undefined_variables(code, file_path))
        issues.extend(self._check_type_consistency(code, file_path))
        issues.extend(self._check_logic_errors(code, file_path))
        issues.extend(self._check_resource_management(code, file_path))

        return issues

    def _check_undefined_variables(self, code: str, file_path: str) -> list[VerificationIssue]:
        """Check for undefined variables"""
        issues: list[VerificationIssue] = []

        try:
            tree = ast.parse(code)
            defined_names: set[str] = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    defined_names.update(arg.arg for arg in node.args.args)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            defined_names.add(target.id)
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    if node.id not in defined_names and not node.id.startswith("_"):
                        # Check if it's a builtin
                        if node.id not in dir(__builtins__):
                            issues.append(
                                VerificationIssue(
                                    result=VerificationResult.WARNING,
                                    category="undefined_variable",
                                    message=f"Potentially undefined variable: {node.id}",
                                    location=file_path,
                                )
                            )
        except Exception:
            pass  # Skip if AST parsing fails

        return issues

    def _check_type_consistency(self, code: str, file_path: str) -> list[VerificationIssue]:
        """Check for type consistency issues"""
        issues: list[VerificationIssue] = []

        # Check for common type mismatches
        type_patterns = [
            (r"str\s*\+\s*int", "String and integer concatenation"),
            (r"len\s*\(\s*int", "len() called on integer"),
            (r"\.append\s*\(\s*[^)]*\[\s*\]", "Appending list to list (use extend)"),
        ]

        for pattern, message in type_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                line_num = code[: match.start()].count("\n") + 1
                issues.append(
                    VerificationIssue(
                        result=VerificationResult.WARNING,
                        category="type_consistency",
                        message=message,
                        location=f"{file_path}:{line_num}",
                        code_snippet=match.group(0),
                    )
                )

        return issues

    def _check_logic_errors(self, code: str, file_path: str) -> list[VerificationIssue]:
        """Check for logic errors"""
        issues: list[VerificationIssue] = []

        # Check for unreachable code
        return_pattern = r"return\s+[^\n]+\n\s+[^\s]"
        matches = re.finditer(return_pattern, code, re.MULTILINE)
        for match in matches:
            line_num = code[: match.start()].count("\n") + 1
            issues.append(
                VerificationIssue(
                    result=VerificationResult.WARNING,
                    category="logic",
                    message="Unreachable code after return statement",
                    location=f"{file_path}:{line_num}",
                )
            )

        # Check for infinite loops
        while_pattern = r"while\s+True\s*:"
        matches = re.finditer(while_pattern, code, re.IGNORECASE)
        for match in matches:
            line_num = code[: match.start()].count("\n") + 1
            # Check if there's a break in the loop body
            loop_body_start = match.end()
            next_indent = len(code[loop_body_start:].split("\n")[0]) - len(
                code[loop_body_start:].split("\n")[0].lstrip()
            )
            loop_body = ""
            for line in code[loop_body_start:].split("\n")[1:10]:
                if line.strip() and len(line) - len(line.lstrip()) <= next_indent:
                    break
                loop_body += line + "\n"

            if "break" not in loop_body.lower():
                issues.append(
                    VerificationIssue(
                        result=VerificationResult.WARNING,
                        category="logic",
                        message="Potential infinite loop without break statement",
                        location=f"{file_path}:{line_num}",
                    )
                )

        return issues

    def _check_resource_management(self, code: str, file_path: str) -> list[VerificationIssue]:
        """Check for resource management issues"""
        issues: list[VerificationIssue] = []

        # Check for file operations without context managers
        file_open_pattern = r"open\s*\([^)]+\)\s*(?!.*with)"
        matches = re.finditer(file_open_pattern, code)
        for match in matches:
            line_num = code[: match.start()].count("\n") + 1
            issues.append(
                VerificationIssue(
                    result=VerificationResult.WARNING,
                    category="resource_management",
                    message="File opened without context manager (use 'with' statement)",
                    location=f"{file_path}:{line_num}",
                    code_snippet=match.group(0),
                )
            )

        return issues

    def validate_solution(
        self, solution: dict[str, Any], requirements: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate solution against requirements"""
        validation_result = {
            "valid": True,
            "issues": [],
            "coverage": {},
        }

        # Check requirement coverage
        required_keys = requirements.get("required_keys", [])
        solution_keys = list(solution.keys())

        missing_keys = [key for key in required_keys if key not in solution_keys]
        if missing_keys:
            validation_result["valid"] = False
            validation_result["issues"].append(
                {
                    "type": "missing_requirements",
                    "message": f"Missing required keys: {', '.join(missing_keys)}",
                }
            )

        # Check data types
        type_requirements = requirements.get("type_requirements", {})
        for key, expected_type in type_requirements.items():
            if key in solution:
                actual_value = solution[key]
                if not isinstance(actual_value, expected_type):
                    validation_result["valid"] = False
                    validation_result["issues"].append(
                        {
                            "type": "type_mismatch",
                            "message": f"{key} expected {expected_type.__name__}, got {type(actual_value).__name__}",
                        }
                    )

        # Calculate coverage
        validation_result["coverage"] = {
            "required_keys": len(required_keys) - len(missing_keys),
            "total_required": len(required_keys),
            "coverage_percentage": (
                (len(required_keys) - len(missing_keys)) / len(required_keys) * 100
                if required_keys
                else 100
            ),
        }

        return validation_result

    def safety_check(self, code: str, operation: str) -> dict[str, Any]:
        """Perform safety checks before execution"""
        safety_result = {
            "safe": True,
            "warnings": [],
            "blocked": False,
        }

        # Check for dangerous operations
        dangerous_patterns = [
            (r"rm\s+-rf|shutil\.rmtree", "Dangerous file deletion operation"),
            (r"eval\s*\(", "Use of eval() - security risk"),
            (r"exec\s*\(", "Use of exec() - security risk"),
            (r"__import__\s*\(", "Dynamic import - potential security risk"),
            (r"subprocess\.call|os\.system", "System command execution"),
        ]

        for pattern, warning in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                safety_result["warnings"].append(warning)
                if "rm" in pattern or "rmtree" in pattern:
                    safety_result["blocked"] = True
                    safety_result["safe"] = False

        # Check for resource limits
        if len(code) > 1000000:  # 1MB limit
            safety_result["warnings"].append("Code size exceeds recommended limit")

        return safety_result

    def rollback_check(self, changes: list[dict[str, Any]]) -> dict[str, Any]:
        """Check if rollback is possible"""
        rollback_info = {
            "rollback_possible": True,
            "rollback_strategy": [],
            "backup_required": False,
        }

        for change in changes:
            change_type = change.get("type", "unknown")

            if change_type == "file_delete":
                rollback_info["backup_required"] = True
                rollback_info["rollback_strategy"].append(
                    {
                        "action": "restore_file",
                        "file": change.get("file"),
                        "backup": change.get("backup"),
                    }
                )
            elif change_type == "file_modify":
                rollback_info["rollback_strategy"].append(
                    {
                        "action": "restore_content",
                        "file": change.get("file"),
                        "original_content": change.get("original_content"),
                    }
                )
            elif change_type == "file_create":
                rollback_info["rollback_strategy"].append(
                    {
                        "action": "delete_file",
                        "file": change.get("file"),
                    }
                )

        return rollback_info

    def get_verification_stats(self) -> dict[str, Any]:
        """Get verification statistics"""
        result_counts = {
            VerificationResult.PASS: 0,
            VerificationResult.FAIL: 0,
            VerificationResult.WARNING: 0,
        }

        for issue in self.verification_history:
            result_counts[issue.result] = result_counts.get(issue.result, 0) + 1

        return {
            "total_verifications": len(self.verification_history),
            "result_counts": {k.value: v for k, v in result_counts.items()},
            "pass_rate": (
                result_counts[VerificationResult.PASS] / len(self.verification_history) * 100
                if self.verification_history
                else 0
            ),
        }
