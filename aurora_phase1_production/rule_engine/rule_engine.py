#!/usr/bin/env python3
"""
Aurora Phase-1 Rule Engine
Severity scoring and rule-based decision engine.
"""

import json
import operator
import re
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class Rule:
    id: str
    name: str
    condition: str
    severity: int
    action: str
    description: str = ""
    category: str = "default"
    enabled: bool = True
    metadata: dict = field(default_factory=dict)


@dataclass
class RuleResult:
    rule_id: str
    rule_name: str
    matched: bool
    severity: int
    action: str
    context: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class EvaluationResult:
    total_rules: int
    rules_matched: int
    max_severity: int
    total_severity: int
    recommended_action: str
    results: list[RuleResult] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class ConditionParser:
    """Parse and evaluate rule conditions"""

    OPERATORS = {
        "==": operator.eq,
        "!=": operator.ne,
        ">": operator.gt,
        ">=": operator.ge,
        "<": operator.lt,
        "<=": operator.le,
        "in": lambda a, b: a in b,
        "not_in": lambda a, b: a not in b,
        "contains": lambda a, b: b in str(a),
        "matches": lambda a, b: bool(re.search(b, str(a))),
        "startswith": lambda a, b: str(a).startswith(b),
        "endswith": lambda a, b: str(a).endswith(b),
    }

    def __init__(self):
        self.operators = self.OPERATORS.copy()

    def parse(self, condition: str) -> tuple[str, str, Any]:
        """Parse condition string into (field, operator, value)"""
        for op_str in sorted(self.operators.keys(), key=len, reverse=True):
            if f" {op_str} " in condition:
                parts = condition.split(f" {op_str} ", 1)
                if len(parts) == 2:
                    field = parts[0].strip()
                    value_str = parts[1].strip()

                    value = self._parse_value(value_str)
                    return field, op_str, value

        return condition, "exists", True

    def _parse_value(self, value_str: str) -> Any:
        """Parse value string into appropriate type"""
        if value_str.startswith('"') and value_str.endswith('"'):
            return value_str[1:-1]
        if value_str.startswith("'") and value_str.endswith("'"):
            return value_str[1:-1]
        if value_str.lower() == "true":
            return True
        if value_str.lower() == "false":
            return False
        if value_str.lower() == "none" or value_str.lower() == "null":
            return None
        if value_str.startswith("[") and value_str.endswith("]"):
            try:
                return json.loads(value_str)
            except json.JSONDecodeError:
                return value_str
        try:
            if "." in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            return value_str

    def evaluate(self, condition: str, context: dict) -> bool:
        """Evaluate a condition against context"""
        parts = condition.split(" and ")
        if len(parts) > 1:
            return all(self.evaluate(p.strip(), context) for p in parts)

        parts = condition.split(" or ")
        if len(parts) > 1:
            return any(self.evaluate(p.strip(), context) for p in parts)

        field, op, expected = self.parse(condition)

        actual = self._get_nested_value(context, field)

        if op == "exists":
            return actual is not None

        if actual is None:
            return False

        op_func = self.operators.get(op)
        if op_func:
            try:
                return op_func(actual, expected)
            except (TypeError, ValueError):
                return False

        return False

    def _get_nested_value(self, context: dict, field: str) -> Any:
        """Get value from nested dict using dot notation"""
        parts = field.split(".")
        value = context

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif hasattr(value, part):
                value = getattr(value, part)
            else:
                return None

            if value is None:
                return None

        return value


class RuleEngine:
    """Rule-based decision engine with severity scoring"""

    DEFAULT_RULES = [
        Rule(
            id="R001",
            name="critical_error",
            condition="severity >= 9",
            severity=10,
            action="disable",
            description="Critical error detected, disable module immediately",
            category="error",
        ),
        Rule(
            id="R002",
            name="high_severity_error",
            condition="severity >= 7 and severity < 9",
            severity=8,
            action="rollback",
            description="High severity error, rollback to last known good state",
            category="error",
        ),
        Rule(
            id="R003",
            name="medium_severity_error",
            condition="severity >= 4 and severity < 7",
            severity=5,
            action="regenerate",
            description="Medium severity error, attempt regeneration",
            category="error",
        ),
        Rule(
            id="R004",
            name="low_severity_error",
            condition="severity >= 1 and severity < 4",
            severity=2,
            action="notify",
            description="Low severity issue, notify for review",
            category="warning",
        ),
        Rule(
            id="R005",
            name="repeated_failures",
            condition="failure_count >= 3",
            severity=7,
            action="disable",
            description="Module has failed 3+ times, disable for investigation",
            category="reliability",
        ),
        Rule(
            id="R006",
            name="timeout_pattern",
            condition="timeout_count >= 2 and execution_time > 5000",
            severity=6,
            action="optimize",
            description="Repeated timeouts detected, optimization needed",
            category="performance",
        ),
        Rule(
            id="R007",
            name="memory_exceeded",
            condition="memory_usage > 128",
            severity=7,
            action="restart",
            description="Memory usage exceeds limit",
            category="resource",
        ),
        Rule(
            id="R008",
            name="inspection_failed",
            condition="inspection_passed == false",
            severity=8,
            action="reject",
            description="Code inspection failed, reject module",
            category="security",
        ),
        Rule(
            id="R009",
            name="test_failure",
            condition="test_passed == false",
            severity=6,
            action="debug",
            description="Test execution failed",
            category="quality",
        ),
        Rule(
            id="R010",
            name="security_violation",
            condition="security_score < 50",
            severity=9,
            action="quarantine",
            description="Security score too low, quarantine module",
            category="security",
        ),
    ]

    ACTION_PRIORITY = {
        "disable": 100,
        "quarantine": 95,
        "reject": 90,
        "rollback": 80,
        "restart": 70,
        "regenerate": 60,
        "optimize": 50,
        "debug": 40,
        "notify": 20,
        "log": 10,
        "ignore": 0,
    }

    def __init__(self, rules: list[Rule] = None, use_defaults: bool = True):
        self.rules = []
        self.parser = ConditionParser()
        self.results_history = []

        if use_defaults:
            self.rules.extend(self.DEFAULT_RULES)

        if rules:
            self.rules.extend(rules)

    def add_rule(self, rule: Rule):
        """Add a rule to the engine"""
        self.rules.append(rule)

    def remove_rule(self, rule_id: str):
        """Remove a rule by ID"""
        self.rules = [r for r in self.rules if r.id != rule_id]

    def get_rule(self, rule_id: str) -> Rule | None:
        """Get a rule by ID"""
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        return None

    def enable_rule(self, rule_id: str, enabled: bool = True):
        """Enable or disable a rule"""
        rule = self.get_rule(rule_id)
        if rule:
            rule.enabled = enabled

    def evaluate(self, context: dict) -> EvaluationResult:
        """Evaluate all rules against context"""
        results = []
        max_severity = 0
        total_severity = 0
        highest_action = "ignore"
        highest_priority = 0

        for rule in self.rules:
            if not rule.enabled:
                continue

            matched = self.parser.evaluate(rule.condition, context)

            result = RuleResult(
                rule_id=rule.id,
                rule_name=rule.name,
                matched=matched,
                severity=rule.severity if matched else 0,
                action=rule.action if matched else "none",
                context={
                    "condition": rule.condition,
                    "category": rule.category,
                    "description": rule.description,
                },
            )

            results.append(result)

            if matched:
                if rule.severity > max_severity:
                    max_severity = rule.severity
                total_severity += rule.severity

                action_priority = self.ACTION_PRIORITY.get(rule.action, 0)
                if action_priority > highest_priority:
                    highest_priority = action_priority
                    highest_action = rule.action

        evaluation = EvaluationResult(
            total_rules=len(self.rules),
            rules_matched=sum(1 for r in results if r.matched),
            max_severity=max_severity,
            total_severity=total_severity,
            recommended_action=highest_action,
            results=results,
        )

        self.results_history.append(evaluation)

        return evaluation

    def calculate_severity_score(self, issues: list[dict]) -> dict:
        """Calculate aggregated severity score from issues list"""
        if not issues:
            return {
                "score": 100,
                "max_severity": 0,
                "total_severity": 0,
                "issue_count": 0,
                "grade": "A+",
            }

        max_sev = 0
        total_sev = 0
        weighted_sum = 0

        severity_weights = {10: 50, 9: 30, 8: 20, 7: 15, 6: 10, 5: 7, 4: 5, 3: 3, 2: 2, 1: 1}

        for issue in issues:
            sev = issue.get("severity", 0)
            max_sev = max(max_sev, sev)
            total_sev += sev
            weighted_sum += severity_weights.get(sev, 0)

        score = max(0, 100 - weighted_sum)

        if score >= 95:
            grade = "A+"
        elif score >= 90:
            grade = "A"
        elif score >= 85:
            grade = "A-"
        elif score >= 80:
            grade = "B+"
        elif score >= 75:
            grade = "B"
        elif score >= 70:
            grade = "B-"
        elif score >= 65:
            grade = "C+"
        elif score >= 60:
            grade = "C"
        elif score >= 55:
            grade = "C-"
        elif score >= 50:
            grade = "D"
        else:
            grade = "F"

        return {
            "score": score,
            "max_severity": max_sev,
            "total_severity": total_sev,
            "issue_count": len(issues),
            "grade": grade,
        }

    def determine_action(self, severity: int) -> str:
        """Determine recommended action based on severity level"""
        if severity >= 9:
            return "disable"
        elif severity >= 7:
            return "rollback"
        elif severity >= 5:
            return "regenerate"
        elif severity >= 3:
            return "debug"
        elif severity >= 1:
            return "notify"
        else:
            return "ignore"

    def export_rules(self, filepath: str):
        """Export rules to JSON file"""
        rules_data = [asdict(r) for r in self.rules]
        with open(filepath, "w") as f:
            json.dump(rules_data, f, indent=2)

    def import_rules(self, filepath: str):
        """Import rules from JSON file"""
        with open(filepath) as f:
            rules_data = json.load(f)

        for rule_dict in rules_data:
            rule = Rule(**rule_dict)
            self.add_rule(rule)

    def get_statistics(self) -> dict:
        """Get statistics from evaluation history"""
        if not self.results_history:
            return {"evaluations": 0}

        total_evals = len(self.results_history)
        total_matches = sum(r.rules_matched for r in self.results_history)
        actions = {}

        for result in self.results_history:
            action = result.recommended_action
            actions[action] = actions.get(action, 0) + 1

        return {
            "evaluations": total_evals,
            "total_matches": total_matches,
            "avg_matches_per_eval": total_matches / total_evals if total_evals > 0 else 0,
            "actions_taken": actions,
            "rules_count": len(self.rules),
            "enabled_rules": sum(1 for r in self.rules if r.enabled),
        }


def create_engine(rules: list[Rule] = None, use_defaults: bool = True) -> RuleEngine:
    return RuleEngine(rules=rules, use_defaults=use_defaults)


if __name__ == "__main__":
    engine = RuleEngine()

    context1 = {
        "severity": 8,
        "failure_count": 1,
        "timeout_count": 0,
        "execution_time": 1000,
        "memory_usage": 64,
        "inspection_passed": True,
        "test_passed": True,
        "security_score": 85,
    }

    result1 = engine.evaluate(context1)
    print("Scenario 1 - High severity error:")
    print(f"  Rules matched: {result1.rules_matched}")
    print(f"  Max severity: {result1.max_severity}")
    print(f"  Recommended action: {result1.recommended_action}")

    context2 = {
        "severity": 5,
        "failure_count": 4,
        "timeout_count": 3,
        "execution_time": 6000,
        "memory_usage": 150,
        "inspection_passed": True,
        "test_passed": False,
        "security_score": 75,
    }

    result2 = engine.evaluate(context2)
    print("\nScenario 2 - Multiple issues:")
    print(f"  Rules matched: {result2.rules_matched}")
    print(f"  Max severity: {result2.max_severity}")
    print(f"  Recommended action: {result2.recommended_action}")

    issues = [
        {"severity": 8, "pattern": "subprocess_import"},
        {"severity": 5, "pattern": "file_open"},
        {"severity": 2, "pattern": "print_statement"},
    ]

    score_result = engine.calculate_severity_score(issues)
    print("\nSeverity scoring:")
    print(f"  Score: {score_result['score']}")
    print(f"  Grade: {score_result['grade']}")
    print(f"  Max severity: {score_result['max_severity']}")

    print(f"\nStatistics: {engine.get_statistics()}")
