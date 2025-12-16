#!/usr/bin/env python3
"""
Aurora Phase-1 Static Code Inspector
Performs banned-pattern checks, complexity analysis, and security scanning.
"""
import ast
import re
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field


@dataclass
class InspectionIssue:
    pattern: str
    severity: int
    line: int
    column: int
    content: str
    category: str
    message: str


@dataclass
class InspectionResult:
    path: str
    safe: bool
    issues: List[Dict] = field(default_factory=list)
    issue_count: int = 0
    max_severity: int = 0
    metrics: Dict = field(default_factory=dict)
    score: float = 100.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    error: Optional[str] = None


class PatternChecker:
    """Check code for banned patterns"""
    
    BANNED_PATTERNS = [
        (r'\bimport\s+os\b', "os_import", 8, "security", "Direct os import detected"),
        (r'\bimport\s+sys\b', "sys_import", 6, "security", "Direct sys import detected"),
        (r'\bimport\s+subprocess\b', "subprocess_import", 10, "security", "Subprocess import detected"),
        (r'\beval\s*\(', "eval_usage", 9, "security", "eval() usage detected"),
        (r'\bexec\s*\(', "exec_usage", 9, "security", "exec() usage detected"),
        (r'\b__import__\s*\(', "dynamic_import", 8, "security", "Dynamic import detected"),
        (r'\bos\.system\s*\(', "os_system", 10, "security", "os.system() call detected"),
        (r'\bos\.popen\s*\(', "os_popen", 10, "security", "os.popen() call detected"),
        (r'\bos\.exec', "os_exec", 10, "security", "os.exec* call detected"),
        (r'\bos\.spawn', "os_spawn", 10, "security", "os.spawn* call detected"),
        (r'\bsubprocess\.', "subprocess_call", 9, "security", "subprocess call detected"),
        (r'\bpickle\.loads?\s*\(', "pickle_loads", 7, "security", "pickle deserialization detected"),
        (r'\bsocket\.', "socket_usage", 7, "network", "Socket usage detected"),
        (r'\burllib\.', "urllib_usage", 5, "network", "urllib usage detected"),
        (r'\brequests\.', "requests_usage", 5, "network", "requests library usage"),
        (r'\bopen\s*\([^)]*["\']w', "file_write", 6, "io", "File write operation detected"),
        (r'\bshutil\.', "shutil_usage", 7, "io", "shutil operations detected"),
        (r'\.rm\s*\(', "rm_call", 8, "io", "File removal detected"),
        (r'\.unlink\s*\(', "unlink_call", 8, "io", "File unlink detected"),
        (r'\bctypes\.', "ctypes_usage", 9, "security", "ctypes usage detected"),
        (r'\b__builtins__', "builtins_access", 8, "security", "Builtins access detected"),
        (r'\bglobals\s*\(\)', "globals_call", 7, "security", "globals() call detected"),
        (r'\blocals\s*\(\)', "locals_call", 5, "security", "locals() call detected"),
        (r'\bsetattr\s*\(', "setattr_usage", 5, "dynamic", "Dynamic attribute setting"),
        (r'\bdelattr\s*\(', "delattr_usage", 5, "dynamic", "Dynamic attribute deletion"),
    ]
    
    WARNING_PATTERNS = [
        (r'\btry:\s*$', "bare_try", 2, "quality", "Consider adding specific exception handling"),
        (r'\bexcept:\s*$', "bare_except", 3, "quality", "Bare except clause, specify exception type"),
        (r'\bexcept\s+Exception\s*:', "broad_except", 2, "quality", "Broad exception clause"),
        (r'#\s*TODO', "todo_comment", 1, "quality", "TODO comment found"),
        (r'#\s*FIXME', "fixme_comment", 2, "quality", "FIXME comment found"),
        (r'#\s*HACK', "hack_comment", 2, "quality", "HACK comment found"),
        (r'\bprint\s*\(', "print_statement", 1, "quality", "Print statement (consider logging)"),
        (r'password\s*=\s*["\']', "hardcoded_password", 8, "security", "Hardcoded password detected"),
        (r'api_key\s*=\s*["\']', "hardcoded_api_key", 8, "security", "Hardcoded API key detected"),
        (r'secret\s*=\s*["\']', "hardcoded_secret", 8, "security", "Hardcoded secret detected"),
    ]
    
    def __init__(self):
        self.compiled_banned = [(re.compile(p), n, s, c, m) for p, n, s, c, m in self.BANNED_PATTERNS]
        self.compiled_warnings = [(re.compile(p), n, s, c, m) for p, n, s, c, m in self.WARNING_PATTERNS]
    
    def check(self, code: str) -> List[InspectionIssue]:
        issues = []
        lines = code.split('\n')
        
        for line_no, line in enumerate(lines, 1):
            for pattern, name, severity, category, message in self.compiled_banned:
                match = pattern.search(line)
                if match:
                    issues.append(InspectionIssue(
                        pattern=name,
                        severity=severity,
                        line=line_no,
                        column=match.start(),
                        content=line.strip()[:100],
                        category=category,
                        message=message
                    ))
            
            for pattern, name, severity, category, message in self.compiled_warnings:
                match = pattern.search(line)
                if match:
                    issues.append(InspectionIssue(
                        pattern=name,
                        severity=severity,
                        line=line_no,
                        column=match.start(),
                        content=line.strip()[:100],
                        category=category,
                        message=message
                    ))
        
        return issues


class ASTAnalyzer:
    """Analyze code using AST for structural issues"""
    
    def __init__(self):
        self.issues = []
        self.metrics = {}
    
    def analyze(self, code: str) -> Tuple[List[InspectionIssue], Dict]:
        self.issues = []
        self.metrics = {
            "lines": len(code.split('\n')),
            "functions": 0,
            "classes": 0,
            "imports": 0,
            "complexity": 0,
            "max_depth": 0,
            "docstrings": 0,
        }
        
        try:
            tree = ast.parse(code)
            self._analyze_tree(tree)
            self._check_complexity(tree)
        except SyntaxError as e:
            self.issues.append(InspectionIssue(
                pattern="syntax_error",
                severity=10,
                line=e.lineno or 0,
                column=e.offset or 0,
                content=str(e.msg)[:100],
                category="syntax",
                message=f"Syntax error: {e.msg}"
            ))
        
        return self.issues, self.metrics
    
    def _analyze_tree(self, tree: ast.AST, depth: int = 0):
        self.metrics["max_depth"] = max(self.metrics["max_depth"], depth)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                self.metrics["functions"] += 1
                if ast.get_docstring(node):
                    self.metrics["docstrings"] += 1
            elif isinstance(node, ast.ClassDef):
                self.metrics["classes"] += 1
                if ast.get_docstring(node):
                    self.metrics["docstrings"] += 1
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                self.metrics["imports"] += 1
    
    def _check_complexity(self, tree: ast.AST):
        complexity = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try,
                                ast.ExceptHandler, ast.With, ast.Assert)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        self.metrics["complexity"] = complexity
        
        if complexity > 20:
            self.issues.append(InspectionIssue(
                pattern="high_complexity",
                severity=4,
                line=1,
                column=0,
                content=f"Cyclomatic complexity: {complexity}",
                category="quality",
                message=f"High cyclomatic complexity ({complexity}), consider refactoring"
            ))


class CodeInspector:
    """Main code inspector combining pattern checking and AST analysis"""
    
    def __init__(self, strict: bool = False):
        self.strict = strict
        self.pattern_checker = PatternChecker()
        self.ast_analyzer = ASTAnalyzer()
        self.results_cache = {}
    
    def inspect(self, module_path: str) -> InspectionResult:
        """Inspect a module file"""
        path = Path(module_path)
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            return self.inspect_code(code, str(path))
            
        except FileNotFoundError:
            return InspectionResult(
                path=str(path),
                safe=False,
                error=f"File not found: {path}"
            )
        except Exception as e:
            return InspectionResult(
                path=str(path),
                safe=False,
                error=str(e)
            )
    
    def inspect_code(self, code: str, path: str = "<code>") -> InspectionResult:
        """Inspect code string directly"""
        pattern_issues = self.pattern_checker.check(code)
        ast_issues, metrics = self.ast_analyzer.analyze(code)
        
        all_issues = pattern_issues + ast_issues
        
        all_issues_dict = [asdict(issue) for issue in all_issues]
        
        max_severity = max([i.severity for i in all_issues], default=0)
        
        safety_threshold = 5 if self.strict else 7
        safe = max_severity < safety_threshold
        
        score = self._calculate_score(all_issues, metrics)
        
        return InspectionResult(
            path=path,
            safe=safe,
            issues=all_issues_dict,
            issue_count=len(all_issues),
            max_severity=max_severity,
            metrics=metrics,
            score=score
        )
    
    def _calculate_score(self, issues: List[InspectionIssue], metrics: Dict) -> float:
        """Calculate a quality score from 0-100"""
        score = 100.0
        
        for issue in issues:
            if issue.severity >= 9:
                score -= 20
            elif issue.severity >= 7:
                score -= 10
            elif issue.severity >= 5:
                score -= 5
            elif issue.severity >= 3:
                score -= 2
            else:
                score -= 1
        
        if metrics.get("complexity", 0) > 15:
            score -= 5
        if metrics.get("complexity", 0) > 25:
            score -= 10
        
        total_funcs = metrics.get("functions", 0) + metrics.get("classes", 0)
        if total_funcs > 0:
            docstring_ratio = metrics.get("docstrings", 0) / total_funcs
            if docstring_ratio < 0.5:
                score -= 5
        
        return max(0.0, min(100.0, score))
    
    def inspect_directory(self, dir_path: str, pattern: str = "*.py") -> List[InspectionResult]:
        """Inspect all Python files in a directory"""
        results = []
        path = Path(dir_path)
        
        for file_path in path.rglob(pattern):
            result = self.inspect(str(file_path))
            results.append(result)
            self.results_cache[str(file_path)] = result
        
        return results
    
    def get_summary(self, results: List[InspectionResult]) -> Dict:
        """Get summary of inspection results"""
        total = len(results)
        safe_count = sum(1 for r in results if r.safe)
        total_issues = sum(r.issue_count for r in results)
        avg_score = sum(r.score for r in results) / total if total > 0 else 0
        
        severity_counts = {}
        category_counts = {}
        
        for result in results:
            for issue in result.issues:
                sev = issue.get("severity", 0)
                cat = issue.get("category", "unknown")
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
                category_counts[cat] = category_counts.get(cat, 0) + 1
        
        return {
            "total_files": total,
            "safe_files": safe_count,
            "unsafe_files": total - safe_count,
            "pass_rate": (safe_count / total * 100) if total > 0 else 0,
            "total_issues": total_issues,
            "average_score": round(avg_score, 2),
            "issues_by_severity": severity_counts,
            "issues_by_category": category_counts,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


def create_inspector(strict: bool = False) -> CodeInspector:
    return CodeInspector(strict=strict)


if __name__ == "__main__":
    inspector = CodeInspector()
    
    test_code = '''
import time

class MyProcessor:
    """Process data efficiently"""
    
    def __init__(self, config=None):
        self.config = config or {}
    
    def process(self, data):
        start = time.time()
        result = self._transform(data)
        return {"result": result, "duration": time.time() - start}
    
    def _transform(self, data):
        return {"processed": True, "input": data}

def execute(payload=None):
    processor = MyProcessor()
    return processor.process(payload or {})
'''
    
    result = inspector.inspect_code(test_code, "test_module.py")
    print(f"Safe: {result.safe}")
    print(f"Score: {result.score}")
    print(f"Issues: {result.issue_count}")
    print(f"Metrics: {result.metrics}")
    
    if result.issues:
        print("\nIssues found:")
        for issue in result.issues:
            print(f"  - Line {issue['line']}: {issue['message']} (severity: {issue['severity']})")
