import ast
import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PatternDetector:
    UNSAFE_PATTERNS = [
        (r'eval\s*\(', 'eval_usage', 8),
        (r'exec\s*\(', 'exec_usage', 8),
        (r'__import__\s*\(', 'dynamic_import', 7),
        (r'subprocess', 'subprocess_usage', 9),
        (r'os\.system', 'os_system', 9),
        (r'open\s*\(.+w', 'file_write', 6),
        (r'pickle\.loads?', 'pickle_usage', 7),
        (r'yaml\.load\s*\(', 'unsafe_yaml', 6),
    ]
    INEFFICIENCY_PATTERNS = [
        (r'for .+ in range\(len\(.+\)\)', 'range_len_antipattern', 2),
        (r'== True|== False', 'explicit_bool_compare', 1),
        (r'\+= .+\n.*\+= ', 'string_concat_loop', 3),
        (r'except:\s*\n\s*pass', 'bare_except_pass', 4),
        (r'global\s+\w+', 'global_usage', 2),
    ]

    def detect(self, code):
        unsafe = []
        inefficient = []
        for pattern, name, severity in self.UNSAFE_PATTERNS:
            matches = re.finditer(pattern, code)
            for m in matches:
                unsafe.append({"pattern": name, "severity": severity, "position": m.start(), "match": m.group()[:50]})
        for pattern, name, severity in self.INEFFICIENCY_PATTERNS:
            matches = re.finditer(pattern, code)
            for m in matches:
                inefficient.append({"pattern": name, "severity": severity, "position": m.start(), "match": m.group()[:50]})
        return {"unsafe": unsafe, "inefficient": inefficient}

class ASTAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.metrics = {"functions": 0, "classes": 0, "imports": 0, "try_blocks": 0, "loops": 0, "conditionals": 0, "complexity": 0}
        self.issues = []

    def visit_FunctionDef(self, node):
        self.metrics["functions"] += 1
        if len(node.body) > 50:
            self.issues.append({"type": "long_function", "name": node.name, "lines": len(node.body), "severity": 3})
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.metrics["classes"] += 1
        self.generic_visit(node)

    def visit_Import(self, node):
        self.metrics["imports"] += 1
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        self.metrics["imports"] += 1
        self.generic_visit(node)

    def visit_Try(self, node):
        self.metrics["try_blocks"] += 1
        for handler in node.handlers:
            if handler.type is None:
                self.issues.append({"type": "bare_except", "severity": 4})
        self.generic_visit(node)

    def visit_For(self, node):
        self.metrics["loops"] += 1
        self.metrics["complexity"] += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.metrics["loops"] += 1
        self.metrics["complexity"] += 1
        self.generic_visit(node)

    def visit_If(self, node):
        self.metrics["conditionals"] += 1
        self.metrics["complexity"] += 1
        self.generic_visit(node)

class StaticInspector:
    def __init__(self):
        self.pattern_detector = PatternDetector()

    def inspect(self, path):
        try:
            with open(path, 'r') as f:
                code = f.read()
        except Exception as e:
            return {"error": str(e), "severity": 10}
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {"syntax_error": str(e), "severity": 10, "line": e.lineno}
        analyzer = ASTAnalyzer()
        analyzer.visit(tree)
        patterns = self.pattern_detector.detect(code)
        all_issues = analyzer.issues + patterns["unsafe"] + patterns["inefficient"]
        max_severity = max((i.get("severity", 0) for i in all_issues), default=0)
        return {"path": path, "metrics": analyzer.metrics, "issues": all_issues, "patterns": patterns, "severity": max_severity, "recommendations": self._generate_recommendations(all_issues)}

    def _generate_recommendations(self, issues):
        recs = []
        for issue in issues:
            pattern = issue.get("pattern") or issue.get("type")
            if pattern == "eval_usage":
                recs.append("Replace eval() with ast.literal_eval() or explicit parsing")
            elif pattern == "exec_usage":
                recs.append("Avoid exec(); use explicit function calls")
            elif pattern == "bare_except":
                recs.append("Use specific exception types instead of bare except")
            elif pattern == "long_function":
                recs.append(f"Refactor function into smaller units")
            elif pattern == "subprocess_usage":
                recs.append("Review subprocess usage for security implications")
        return list(set(recs))

    def inspect_batch(self, paths):
        return [self.inspect(p) for p in paths]
