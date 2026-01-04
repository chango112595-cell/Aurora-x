import json
from pathlib import Path

class SeverityRule:
    def __init__(self, name, pattern, base_severity, modifiers=None):
        self.name = name
        self.pattern = pattern
        self.base_severity = base_severity
        self.modifiers = modifiers or {}

    def evaluate(self, context):
        severity = self.base_severity
        for key, modifier in self.modifiers.items():
            if key in context:
                severity += modifier
        return min(10, max(0, severity))

class RuleEngine:
    DEFAULT_RULES = [
        SeverityRule("syntax_error", "syntax", 10),
        SeverityRule("security_violation", "security", 9, {"in_production": 1}),
        SeverityRule("performance_issue", "performance", 5, {"critical_path": 2}),
        SeverityRule("test_failure", "test", 6, {"regression": 2}),
        SeverityRule("code_quality", "quality", 3),
    ]

    def __init__(self, rules=None):
        self.rules = rules or self.DEFAULT_RULES
        self.rule_map = {r.name: r for r in self.rules}

    def evaluate(self, incident_type, context=None):
        context = context or {}
        for rule in self.rules:
            if rule.pattern in incident_type.lower():
                return rule.evaluate(context)
        return 5

    def should_auto_repair(self, severity):
        return 3 <= severity <= 7

    def requires_approval(self, severity):
        return severity >= 8

    def get_action(self, severity):
        if severity >= 9:
            return "block_and_notify"
        elif severity >= 7:
            return "repair_with_approval"
        elif severity >= 4:
            return "auto_repair"
        else:
            return "log_only"

class CapabilityManager:
    TIERS = {
        "sandbox": ["read", "compute"],
        "worker": ["read", "compute", "write_temp"],
        "autonomy": ["read", "compute", "write_temp", "write_module", "repair"],
        "admin": ["read", "compute", "write_temp", "write_module", "repair", "promote", "delete"]
    }

    def __init__(self):
        self.active_capabilities = {}

    def grant(self, entity_id, tier):
        if tier in self.TIERS:
            self.active_capabilities[entity_id] = set(self.TIERS[tier])

    def check(self, entity_id, capability):
        caps = self.active_capabilities.get(entity_id, set())
        return capability in caps

    def revoke(self, entity_id):
        self.active_capabilities.pop(entity_id, None)
