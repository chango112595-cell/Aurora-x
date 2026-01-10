"""
Predictive Issue Detection System
Self-contained proactive issue prediction using pattern analysis and trend detection
No external APIs - uses statistical analysis and pattern matching
"""

import statistics
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from ..workers.issue_detector import DetectedIssue, IssueCategory, IssueSeverity


class PredictionConfidence(Enum):
    """Confidence levels for predictions"""

    HIGH = "high"  # >80% likelihood
    MEDIUM = "medium"  # 50-80% likelihood
    LOW = "low"  # <50% likelihood


@dataclass
class PredictedIssue:
    """A predicted issue before it occurs"""

    prediction_id: str
    issue_type: str
    predicted_at: datetime
    predicted_occurrence_time: datetime
    confidence: PredictionConfidence
    severity: IssueSeverity
    category: IssueCategory
    indicators: list[str] = field(default_factory=list)
    prevention_suggestions: list[str] = field(default_factory=list)
    likelihood_score: float = 0.0


class PredictiveIssueDetector:
    """
    Self-contained predictive issue detection
    Uses trend analysis, anomaly detection, and pattern recognition
    """

    def __init__(self, history_window_hours: int = 24):
        self.history_window_hours = history_window_hours
        self.issue_history: deque = deque(maxlen=10000)  # Last 10k issues
        self.metric_history: dict[str, deque] = {}  # metric_name -> [values]
        self.pattern_history: dict[str, list[dict[str, Any]]] = {}  # pattern -> [occurrences]
        self.predicted_issues: list[PredictedIssue] = []
        self.anomaly_thresholds: dict[str, float] = {}
        self._initialize_thresholds()

    def _initialize_thresholds(self):
        """Initialize anomaly detection thresholds"""
        self.anomaly_thresholds = {
            "error_rate": 0.1,  # 10% error rate is anomalous
            "response_time_ms": 5000,  # 5s response time is anomalous
            "memory_usage_percent": 90,  # 90% memory is anomalous
            "cpu_usage_percent": 95,  # 95% CPU is anomalous
            "failed_tasks_per_hour": 10,  # 10 failed tasks/hour is anomalous
        }

    def record_issue(self, issue: DetectedIssue):
        """Record an issue for pattern analysis"""
        self.issue_history.append(
            {
                "issue": issue,
                "timestamp": datetime.now(),
                "type": issue.type,
                "category": issue.category.value,
                "severity": issue.severity.value,
            }
        )

        # Update pattern history
        pattern_key = f"{issue.category.value}:{issue.type}"
        if pattern_key not in self.pattern_history:
            self.pattern_history[pattern_key] = []

        self.pattern_history[pattern_key].append(
            {
                "timestamp": datetime.now(),
                "severity": issue.severity.value,
                "target": issue.target,
            }
        )

        # Keep only recent patterns (last 1000 per pattern)
        if len(self.pattern_history[pattern_key]) > 1000:
            self.pattern_history[pattern_key] = self.pattern_history[pattern_key][-1000:]

    def record_metric(self, metric_name: str, value: float):
        """Record a metric value for trend analysis"""
        if metric_name not in self.metric_history:
            self.metric_history[metric_name] = deque(maxlen=10000)

        self.metric_history[metric_name].append(
            {
                "value": value,
                "timestamp": datetime.now(),
            }
        )

    def predict_issues(self) -> list[PredictedIssue]:
        """
        Predict potential issues before they occur
        """

        predictions = []
        now = datetime.now()

        # Method 1: Trend analysis - detect increasing error rates
        trend_predictions = self._predict_from_trends(now)
        predictions.extend(trend_predictions)

        # Method 2: Anomaly detection - detect unusual patterns
        anomaly_predictions = self._predict_from_anomalies(now)
        predictions.extend(anomaly_predictions)

        # Method 3: Pattern matching - detect recurring patterns
        pattern_predictions = self._predict_from_patterns(now)
        predictions.extend(pattern_predictions)

        # Method 4: Resource exhaustion prediction
        resource_predictions = self._predict_resource_exhaustion(now)
        predictions.extend(resource_predictions)

        # Store predictions
        self.predicted_issues.extend(predictions)

        # Keep only recent predictions (last 1000)
        if len(self.predicted_issues) > 1000:
            self.predicted_issues = self.predicted_issues[-1000:]

        return predictions

    def _predict_from_trends(self, now: datetime) -> list[PredictedIssue]:
        """Predict issues from trend analysis"""
        predictions = []

        # Analyze error rate trends
        recent_issues = [
            h
            for h in self.issue_history
            if (now - h["timestamp"]).total_seconds() < self.history_window_hours * 3600
        ]

        if len(recent_issues) < 5:
            return predictions

        # Calculate error rate trend
        hourly_rates = {}
        for issue_record in recent_issues:
            hour_key = issue_record["timestamp"].replace(minute=0, second=0, microsecond=0)
            hourly_rates[hour_key] = hourly_rates.get(hour_key, 0) + 1

        if len(hourly_rates) >= 3:
            rates = list(hourly_rates.values())
            trend = self._calculate_trend(rates)

            # If trend is increasing significantly, predict issue
            if trend > 0.5:  # 50% increase per hour
                prediction = PredictedIssue(
                    prediction_id=str(uuid.uuid4()),
                    issue_type="increasing_error_rate",
                    predicted_at=now,
                    predicted_occurrence_time=now + timedelta(hours=1),
                    confidence=PredictionConfidence.MEDIUM,
                    severity=IssueSeverity.HIGH,
                    category=IssueCategory.SYSTEM,
                    indicators=[f"Error rate increasing at {trend:.1%} per hour"],
                    prevention_suggestions=[
                        "Increase monitoring frequency",
                        "Review recent code changes",
                        "Check system resources",
                    ],
                    likelihood_score=min(trend, 1.0),
                )
                predictions.append(prediction)

        return predictions

    def _predict_from_anomalies(self, now: datetime) -> list[PredictedIssue]:
        """Predict issues from anomaly detection"""
        predictions = []

        # Check each metric for anomalies
        for metric_name, values_deque in self.metric_history.items():
            if len(values_deque) < 10:
                continue

            recent_values = [v["value"] for v in list(values_deque)[-20:]]  # Last 20

            # Calculate baseline (mean of first half)
            baseline = statistics.mean(recent_values[:10])

            # Check if recent values exceed threshold
            threshold = self.anomaly_thresholds.get(metric_name, baseline * 1.5)

            if recent_values[-1] > threshold:
                # Anomaly detected - predict issue
                prediction = PredictedIssue(
                    prediction_id=str(uuid.uuid4()),
                    issue_type=f"{metric_name}_anomaly",
                    predicted_at=now,
                    predicted_occurrence_time=now + timedelta(minutes=30),
                    confidence=PredictionConfidence.HIGH,
                    severity=self._determine_severity_from_metric(metric_name, recent_values[-1]),
                    category=self._determine_category_from_metric(metric_name),
                    indicators=[
                        f"{metric_name} at {recent_values[-1]:.2f} (threshold: {threshold:.2f})"
                    ],
                    prevention_suggestions=self._get_prevention_for_metric(metric_name),
                    likelihood_score=min((recent_values[-1] - threshold) / threshold, 1.0),
                )
                predictions.append(prediction)

        return predictions

    def _predict_from_patterns(self, now: datetime) -> list[PredictedIssue]:
        """Predict issues from recurring patterns"""
        predictions = []

        # Analyze pattern history for recurring issues
        for pattern_key, occurrences in self.pattern_history.items():
            if len(occurrences) < 3:
                continue

            # Check if pattern is recurring
            intervals = []
            for i in range(1, len(occurrences)):
                interval = (
                    occurrences[i]["timestamp"] - occurrences[i - 1]["timestamp"]
                ).total_seconds()
                intervals.append(interval)

            if len(intervals) >= 2:
                avg_interval = statistics.mean(intervals)
                std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0

                # If intervals are relatively consistent, predict next occurrence
                if std_interval < avg_interval * 0.3:  # Low variance = predictable pattern
                    last_occurrence = occurrences[-1]["timestamp"]
                    predicted_time = last_occurrence + timedelta(seconds=avg_interval)

                    if predicted_time > now:  # Future prediction
                        category_str, issue_type = pattern_key.split(":", 1)
                        prediction = PredictedIssue(
                            prediction_id=str(uuid.uuid4()),
                            issue_type=issue_type,
                            predicted_at=now,
                            predicted_occurrence_time=predicted_time,
                            confidence=PredictionConfidence.MEDIUM,
                            severity=IssueSeverity.MEDIUM,
                            category=IssueCategory(category_str),
                            indicators=[
                                (
                                    f"Recurring pattern detected "
                                    f"(avg interval: {avg_interval/3600:.1f}h)"
                                )
                            ],
                            prevention_suggestions=[
                                "Investigate root cause",
                                "Implement preventive measures",
                            ],
                            likelihood_score=0.7,
                        )
                        predictions.append(prediction)

        return predictions

    def _predict_resource_exhaustion(self, now: datetime) -> list[PredictedIssue]:
        """Predict resource exhaustion issues"""
        predictions = []

        # Check memory trend
        if "memory_usage_percent" in self.metric_history:
            memory_values = [
                v["value"] for v in list(self.metric_history["memory_usage_percent"])[-10:]
            ]
            if len(memory_values) >= 5:
                trend = self._calculate_trend(memory_values)

                # If memory is increasing and above 70%, predict exhaustion
                if trend > 0 and memory_values[-1] > 70:
                    hours_to_exhaustion = (
                        (100 - memory_values[-1]) / (trend * memory_values[-1]) if trend > 0 else 24
                    )

                    prediction = PredictedIssue(
                        prediction_id=str(uuid.uuid4()),
                        issue_type="memory_exhaustion",
                        predicted_at=now,
                        predicted_occurrence_time=now
                        + timedelta(hours=max(1, int(hours_to_exhaustion))),
                        confidence=PredictionConfidence.HIGH
                        if memory_values[-1] > 85
                        else PredictionConfidence.MEDIUM,
                        severity=IssueSeverity.HIGH,
                        category=IssueCategory.PERFORMANCE,
                        indicators=[f"Memory at {memory_values[-1]:.1f}% and increasing"],
                        prevention_suggestions=[
                            "Increase memory allocation",
                            "Identify memory leaks",
                            "Optimize memory usage",
                        ],
                        likelihood_score=memory_values[-1] / 100.0,
                    )
                    predictions.append(prediction)

        return predictions

    def _calculate_trend(self, values: list[float]) -> float:
        """Calculate trend (positive = increasing, negative = decreasing)"""
        if len(values) < 2:
            return 0.0

        # Simple linear regression slope
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = statistics.mean(values)

        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        slope = numerator / denominator

        # Normalize to percentage change per unit
        if y_mean != 0:
            return slope / y_mean

        return 0.0

    def _determine_severity_from_metric(self, metric_name: str, value: float) -> IssueSeverity:
        """Determine severity from metric value"""
        threshold = self.anomaly_thresholds.get(metric_name, 0)

        if value > threshold * 1.5:
            return IssueSeverity.CRITICAL
        elif value > threshold * 1.2:
            return IssueSeverity.HIGH
        elif value > threshold:
            return IssueSeverity.MEDIUM
        else:
            return IssueSeverity.LOW

    def _determine_category_from_metric(self, metric_name: str) -> IssueCategory:
        """Determine category from metric name"""
        if "memory" in metric_name or "cpu" in metric_name:
            return IssueCategory.PERFORMANCE
        elif "error" in metric_name or "failure" in metric_name:
            return IssueCategory.SYSTEM
        elif "security" in metric_name:
            return IssueCategory.SECURITY
        else:
            return IssueCategory.SYSTEM

    def _get_prevention_for_metric(self, metric_name: str) -> list[str]:
        """Get prevention suggestions for metric"""
        suggestions_map = {
            "memory_usage_percent": [
                "Increase memory allocation",
                "Identify and fix memory leaks",
                "Optimize memory usage",
            ],
            "cpu_usage_percent": [
                "Optimize CPU-intensive operations",
                "Add more CPU resources",
                "Distribute load",
            ],
            "error_rate": [
                "Review recent changes",
                "Increase error handling",
                "Add monitoring",
            ],
        }

        for key, suggestions in suggestions_map.items():
            if key in metric_name:
                return suggestions

        return ["Monitor closely", "Investigate root cause"]

    def get_predictions(self, min_confidence: PredictionConfidence = None) -> list[PredictedIssue]:
        """Get predicted issues"""
        if min_confidence is None:
            return self.predicted_issues

        confidence_levels = {
            PredictionConfidence.HIGH: 0.8,
            PredictionConfidence.MEDIUM: 0.5,
            PredictionConfidence.LOW: 0.0,
        }

        min_score = confidence_levels.get(min_confidence, 0.0)
        return [p for p in self.predicted_issues if p.likelihood_score >= min_score]

    def get_status(self) -> dict[str, Any]:
        """Get detector status"""
        return {
            "total_issues_recorded": len(self.issue_history),
            "total_predictions": len(self.predicted_issues),
            "metrics_tracked": list(self.metric_history.keys()),
            "patterns_identified": len(self.pattern_history),
            "high_confidence_predictions": len(
                [p for p in self.predicted_issues if p.confidence == PredictionConfidence.HIGH]
            ),
        }
