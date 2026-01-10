"""
Advanced Security Analysis System
Self-contained deep security analysis with vulnerability detection and threat modeling
No external APIs - uses pattern recognition, risk assessment, and secure coding enforcement
"""

import ast
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any


class Severity(Enum):
    """Security issue severity"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class VulnerabilityType(Enum):
    """Vulnerability types"""

    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    INSECURE_AUTH = "insecure_auth"
    SENSITIVE_DATA_EXPOSURE = "sensitive_data_exposure"
    INSECURE_CONFIG = "insecure_config"
    INSECURE_DEPENDENCY = "insecure_dependency"
    INSECURE_LOG = "insecure_log"
    WEAK_CRYPTO = "weak_crypto"


@dataclass
class SecurityIssue:
    """Security issue"""

    vulnerability_type: VulnerabilityType
    severity: Severity
    location: str
    description: str
    recommendation: str
    code_snippet: str | None = None


class AdvancedSecurityAnalyzer:
    """
    Self-contained advanced security analysis system
    Deep security analysis with vulnerability detection and threat modeling
    """

    def __init__(self):
        # Vulnerability patterns
        self.sql_patterns = [
            r"execute\s*\(\s*['\"].*%.*['\"]",
            r"query\s*\(\s*['\"].*%.*['\"]",
            r"cursor\.execute\s*\(\s*['\"].*%.*['\"]",
            r"\.format\s*\([^)]*sql",
        ]

        self.xss_patterns = [
            r"innerHTML\s*=",
            r"\.html\s*\(",
            r"dangerouslySetInnerHTML",
            r"eval\s*\(",
        ]

        self.insecure_auth_patterns = [
            r"password\s*=\s*['\"][^'\"]*['\"]",
            r"api_key\s*=\s*['\"][^'\"]*['\"]",
            r"secret\s*=\s*['\"][^'\"]*['\"]",
            r"token\s*=\s*['\"][^'\"]*['\"]",
        ]

        self.weak_crypto_patterns = [
            r"md5\s*\(",
            r"sha1\s*\(",
            r"DES\s*\(",
            r"RC4\s*\(",
        ]

        # Secure coding patterns
        self.secure_patterns = {
            "input_validation": r"validate|sanitize|escape",
            "parameterized_queries": r"execute\s*\(\s*\?|%s|:param",
            "csrf_protection": r"csrf_token|csrf_protect",
            "secure_headers": r"X-Content-Type-Options|X-Frame-Options",
        }

    def analyze_code(self, code: str, file_path: str = "") -> list[SecurityIssue]:
        """Analyze code for security vulnerabilities"""
        issues: list[SecurityIssue] = []

        # Check for SQL injection
        issues.extend(self._check_sql_injection(code, file_path))

        # Check for XSS
        issues.extend(self._check_xss(code, file_path))

        # Check for insecure authentication
        issues.extend(self._check_insecure_auth(code, file_path))

        # Check for weak cryptography
        issues.extend(self._check_weak_crypto(code, file_path))

        # Check for sensitive data exposure
        issues.extend(self._check_sensitive_data(code, file_path))

        # Check for insecure configuration
        issues.extend(self._check_insecure_config(code, file_path))

        # Check for insecure logging
        issues.extend(self._check_insecure_logging(code, file_path))

        return issues

    def _check_sql_injection(self, code: str, file_path: str) -> list[SecurityIssue]:
        """Check for SQL injection vulnerabilities"""
        issues: list[SecurityIssue] = []

        for pattern in self.sql_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                line_num = code[: match.start()].count("\n") + 1
                issues.append(
                    SecurityIssue(
                        vulnerability_type=VulnerabilityType.SQL_INJECTION,
                        severity=Severity.HIGH,
                        location=f"{file_path}:{line_num}",
                        description=f"Potential SQL injection vulnerability detected",
                        recommendation="Use parameterized queries or prepared statements",
                        code_snippet=match.group(0),
                    )
                )

        return issues

    def _check_xss(self, code: str, file_path: str) -> list[SecurityIssue]:
        """Check for XSS vulnerabilities"""
        issues: list[SecurityIssue] = []

        for pattern in self.xss_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                line_num = code[: match.start()].count("\n") + 1
                issues.append(
                    SecurityIssue(
                        vulnerability_type=VulnerabilityType.XSS,
                        severity=Severity.HIGH,
                        location=f"{file_path}:{line_num}",
                        description="Potential XSS vulnerability detected",
                        recommendation="Sanitize user input and use safe rendering methods",
                        code_snippet=match.group(0),
                    )
                )

        return issues

    def _check_insecure_auth(self, code: str, file_path: str) -> list[SecurityIssue]:
        """Check for insecure authentication"""
        issues: list[SecurityIssue] = []

        for pattern in self.insecure_auth_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                line_num = code[: match.start()].count("\n") + 1
                issues.append(
                    SecurityIssue(
                        vulnerability_type=VulnerabilityType.INSECURE_AUTH,
                        severity=Severity.CRITICAL,
                        location=f"{file_path}:{line_num}",
                        description="Hardcoded credentials detected",
                        recommendation="Use environment variables or secure credential storage",
                        code_snippet=match.group(0),
                    )
                )

        return issues

    def _check_weak_crypto(self, code: str, file_path: str) -> list[SecurityIssue]:
        """Check for weak cryptography"""
        issues: list[SecurityIssue] = []

        for pattern in self.weak_crypto_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                line_num = code[: match.start()].count("\n") + 1
                issues.append(
                    SecurityIssue(
                        vulnerability_type=VulnerabilityType.WEAK_CRYPTO,
                        severity=Severity.MEDIUM,
                        location=f"{file_path}:{line_num}",
                        description="Weak cryptographic algorithm detected",
                        recommendation="Use strong cryptographic algorithms (SHA-256, AES-256)",
                        code_snippet=match.group(0),
                    )
                )

        return issues

    def _check_sensitive_data(self, code: str, file_path: str) -> list[SecurityIssue]:
        """Check for sensitive data exposure"""
        issues: list[SecurityIssue] = []

        sensitive_patterns = [
            r"password\s*=\s*[^=]+",
            r"ssn\s*=\s*[^=]+",
            r"credit_card\s*=\s*[^=]+",
            r"api_key\s*=\s*[^=]+",
        ]

        for pattern in sensitive_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                line_num = code[: match.start()].count("\n") + 1
                issues.append(
                    SecurityIssue(
                        vulnerability_type=VulnerabilityType.SENSITIVE_DATA_EXPOSURE,
                        severity=Severity.HIGH,
                        location=f"{file_path}:{line_num}",
                        description="Potential sensitive data exposure",
                        recommendation="Encrypt sensitive data and use secure storage",
                        code_snippet=match.group(0),
                    )
                )

        return issues

    def _check_insecure_config(self, code: str, file_path: str) -> list[SecurityIssue]:
        """Check for insecure configuration"""
        issues: list[SecurityIssue] = []

        config_patterns = [
            r"DEBUG\s*=\s*True",
            r"ALLOWED_HOSTS\s*=\s*\[\s*['\"]\*['\"]",
            r"CORS_ORIGIN_ALLOW_ALL\s*=\s*True",
        ]

        for pattern in config_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                line_num = code[: match.start()].count("\n") + 1
                issues.append(
                    SecurityIssue(
                        vulnerability_type=VulnerabilityType.INSECURE_CONFIG,
                        severity=Severity.MEDIUM,
                        location=f"{file_path}:{line_num}",
                        description="Insecure configuration detected",
                        recommendation="Use secure configuration settings",
                        code_snippet=match.group(0),
                    )
                )

        return issues

    def _check_insecure_logging(self, code: str, file_path: str) -> list[SecurityIssue]:
        """Check for insecure logging"""
        issues: list[SecurityIssue] = []

        log_patterns = [
            r"log\s*\([^)]*password[^)]*\)",
            r"log\s*\([^)]*token[^)]*\)",
            r"print\s*\([^)]*password[^)]*\)",
        ]

        for pattern in log_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                line_num = code[: match.start()].count("\n") + 1
                issues.append(
                    SecurityIssue(
                        vulnerability_type=VulnerabilityType.INSECURE_LOG,
                        severity=Severity.MEDIUM,
                        location=f"{file_path}:{line_num}",
                        description="Sensitive data in logging detected",
                        recommendation="Remove sensitive data from logs or mask it",
                        code_snippet=match.group(0),
                    )
                )

        return issues

    def assess_risk(self, issues: list[SecurityIssue]) -> dict[str, Any]:
        """Assess overall security risk"""
        severity_counts = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 0,
            Severity.MEDIUM: 0,
            Severity.LOW: 0,
            Severity.INFO: 0,
        }

        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1

        # Calculate risk score (weighted)
        risk_score = (
            severity_counts[Severity.CRITICAL] * 10
            + severity_counts[Severity.HIGH] * 5
            + severity_counts[Severity.MEDIUM] * 2
            + severity_counts[Severity.LOW] * 1
        )

        # Determine risk level
        if risk_score >= 50:
            risk_level = "CRITICAL"
        elif risk_score >= 20:
            risk_level = "HIGH"
        elif risk_score >= 10:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "severity_counts": {k.value: v for k, v in severity_counts.items()},
            "total_issues": len(issues),
        }

    def model_threats(
        self, code: str, context: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Model potential threats"""
        threats: list[dict[str, Any]] = []

        # Analyze attack surface
        if "user_input" in code.lower():
            threats.append(
                {
                    "threat": "User Input Manipulation",
                    "likelihood": "HIGH",
                    "impact": "HIGH",
                    "mitigation": "Implement input validation and sanitization",
                }
            )

        if "database" in code.lower() or "sql" in code.lower():
            threats.append(
                {
                    "threat": "SQL Injection",
                    "likelihood": "MEDIUM",
                    "impact": "HIGH",
                    "mitigation": "Use parameterized queries",
                }
            )

        if "authentication" in code.lower() or "login" in code.lower():
            threats.append(
                {
                    "threat": "Authentication Bypass",
                    "likelihood": "MEDIUM",
                    "impact": "CRITICAL",
                    "mitigation": "Implement strong authentication and session management",
                }
            )

        return threats

    def enforce_secure_patterns(self, code: str) -> dict[str, Any]:
        """Enforce secure coding patterns"""
        recommendations: list[str] = []

        # Check for input validation
        if not re.search(self.secure_patterns["input_validation"], code, re.IGNORECASE):
            recommendations.append("Add input validation for user inputs")

        # Check for parameterized queries
        if "sql" in code.lower() and not re.search(
            self.secure_patterns["parameterized_queries"], code, re.IGNORECASE
        ):
            recommendations.append("Use parameterized queries for database operations")

        # Check for CSRF protection
        if "form" in code.lower() or "post" in code.lower():
            if not re.search(self.secure_patterns["csrf_protection"], code, re.IGNORECASE):
                recommendations.append("Implement CSRF protection for forms")

        return {
            "recommendations": recommendations,
            "compliance_score": max(0, 100 - len(recommendations) * 20),
        }
