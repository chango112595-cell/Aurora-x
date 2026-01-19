"""
Advanced Analytics & Insights System
Self-contained deep analytics with performance trends, bottleneck identification, and predictions
No external APIs - uses statistical analysis, pattern recognition, and predictive algorithms
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any


@dataclass
class PerformanceMetric:
    """Performance metric"""

    name: str
    value: float
    timestamp: datetime
    metadata: dict[str, Any] | None = None


@dataclass
class Bottleneck:
    """Bottleneck identification"""

    component: str
    severity: str
    impact: float
    description: str
    recommendation: str


class AdvancedAnalytics:
    """
    Self-contained advanced analytics system
    Deep insights with performance trends, bottleneck identification, and predictions
    """

    def __init__(self):
        self.metrics_history: list[PerformanceMetric] = []
        self.bottlenecks: list[Bottleneck] = []
        self.trends: dict[str, dict[str, Any]] = {}

    def record_metric(self, name: str, value: float, metadata: dict[str, Any] | None = None):
        """Record a performance metric"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            metadata=metadata,
        )
        self.metrics_history.append(metric)

        # Keep only recent history (last 50000)
        if len(self.metrics_history) > 50000:
            self.metrics_history = self.metrics_history[-50000:]

    def analyze_trends(self, metric_name: str, window_hours: int = 24) -> dict[str, Any]:
        """Analyze performance trends"""
        cutoff_time = datetime.now() - timedelta(hours=window_hours)
        recent_metrics = [
            m for m in self.metrics_history if m.name == metric_name and m.timestamp >= cutoff_time
        ]

        if len(recent_metrics) < 2:
            return {
                "metric_name": metric_name,
                "trend": "insufficient_data",
                "change_percentage": 0.0,
            }

        # Calculate trend
        values = [m.value for m in recent_metrics]
        first_half = values[: len(values) // 2]
        second_half = values[len(values) // 2 :]

        avg_first = sum(first_half) / len(first_half) if first_half else 0
        avg_second = sum(second_half) / len(second_half) if second_half else 0

        change_percentage = ((avg_second - avg_first) / avg_first * 100) if avg_first != 0 else 0

        if change_percentage > 10:
            trend = "increasing"
        elif change_percentage < -10:
            trend = "decreasing"
        else:
            trend = "stable"

        # Calculate volatility
        if len(values) > 1:
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            volatility = variance**0.5
        else:
            volatility = 0.0

        result = {
            "metric_name": metric_name,
            "trend": trend,
            "change_percentage": change_percentage,
            "volatility": volatility,
            "current_value": values[-1] if values else 0,
            "average_value": sum(values) / len(values) if values else 0,
            "min_value": min(values) if values else 0,
            "max_value": max(values) if values else 0,
        }

        self.trends[metric_name] = result
        return result

    def identify_bottlenecks(self, metrics: dict[str, float]) -> list[Bottleneck]:
        """Identify performance bottlenecks"""
        bottlenecks: list[Bottleneck] = []

        # Define thresholds
        thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "response_time": 1000.0,  # milliseconds
            "error_rate": 5.0,  # percentage
            "queue_length": 100,
        }

        for component, value in metrics.items():
            threshold = thresholds.get(component, 80.0)

            if value > threshold:
                severity = "critical" if value > threshold * 1.5 else "high"
                impact = min(100.0, (value / threshold) * 100)

                bottlenecks.append(
                    Bottleneck(
                        component=component,
                        severity=severity,
                        impact=impact,
                        description=f"{component} exceeds threshold ({value} > {threshold})",
                        recommendation=self._get_bottleneck_recommendation(component, value),
                    )
                )

        self.bottlenecks = bottlenecks
        return bottlenecks

    def _get_bottleneck_recommendation(self, component: str, value: float) -> str:
        """Get recommendation for bottleneck"""
        recommendations = {
            "cpu_usage": "Consider scaling horizontally, optimizing algorithms, or offloading tasks",
            "memory_usage": "Consider memory optimization, caching strategies, or increasing memory",
            "response_time": "Optimize database queries, add caching, or improve algorithm efficiency",
            "error_rate": "Investigate error sources, improve error handling, or add retry logic",
            "queue_length": "Increase processing capacity or optimize task processing",
        }

        return recommendations.get(component, "Investigate and optimize this component")

    def predict_performance(self, metric_name: str, hours_ahead: int = 1) -> dict[str, Any]:
        """Predict future performance"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_metrics = [
            m for m in self.metrics_history if m.name == metric_name and m.timestamp >= cutoff_time
        ]

        if len(recent_metrics) < 3:
            return {
                "metric_name": metric_name,
                "predicted_value": None,
                "confidence": 0.0,
                "prediction_hours": hours_ahead,
            }

        # Simple linear regression for prediction
        values = [m.value for m in recent_metrics]
        timestamps = [
            (m.timestamp - recent_metrics[0].timestamp).total_seconds() / 3600
            for m in recent_metrics
        ]

        # Calculate trend
        n = len(values)
        sum_x = sum(timestamps)
        sum_y = sum(values)
        sum_xy = sum(timestamps[i] * values[i] for i in range(n))
        sum_x2 = sum(t**2 for t in timestamps)

        if n * sum_x2 - sum_x**2 != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
            intercept = (sum_y - slope * sum_x) / n
        else:
            slope = 0
            intercept = values[-1]

        # Predict future value
        future_time = timestamps[-1] + hours_ahead
        predicted_value = slope * future_time + intercept

        # Calculate confidence based on data quality
        variance = (
            sum((values[i] - (slope * timestamps[i] + intercept)) ** 2 for i in range(n)) / n
            if n > 0
            else 0
        )
        confidence = max(
            0.0, min(100.0, 100 - (variance / max(values) * 100) if max(values) > 0 else 100)
        )

        return {
            "metric_name": metric_name,
            "predicted_value": predicted_value,
            "confidence": confidence,
            "prediction_hours": hours_ahead,
            "trend": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
        }

    def get_optimization_recommendations(self) -> list[dict[str, Any]]:
        """Get optimization recommendations"""
        recommendations: list[dict[str, Any]] = []

        # Analyze all trends
        metric_names = set(m.name for m in self.metrics_history[-1000:])

        for metric_name in metric_names:
            trend = self.analyze_trends(metric_name)

            if trend["trend"] == "increasing" and trend["change_percentage"] > 20:
                recommendations.append(
                    {
                        "metric": metric_name,
                        "priority": "high",
                        "recommendation": f"Consider optimizing {metric_name} - showing {trend['change_percentage']:.1f}% increase",
                        "impact": "high",
                    }
                )

        # Add bottleneck recommendations
        for bottleneck in self.bottlenecks:
            recommendations.append(
                {
                    "metric": bottleneck.component,
                    "priority": bottleneck.severity,
                    "recommendation": bottleneck.recommendation,
                    "impact": "critical" if bottleneck.severity == "critical" else "high",
                }
            )

        return recommendations

    def get_insights(self) -> dict[str, Any]:
        """Get comprehensive insights"""
        # Analyze all metrics
        metric_names = set(m.name for m in self.metrics_history[-1000:])

        insights = {
            "total_metrics": len(self.metrics_history),
            "unique_metrics": len(metric_names),
            "trends": {},
            "bottlenecks": len(self.bottlenecks),
            "critical_bottlenecks": len([b for b in self.bottlenecks if b.severity == "critical"]),
            "recommendations": self.get_optimization_recommendations(),
        }

        # Analyze trends for key metrics
        key_metrics = ["cpu_usage", "memory_usage", "response_time", "error_rate", "throughput"]
        for metric_name in key_metrics:
            if metric_name in metric_names:
                insights["trends"][metric_name] = self.analyze_trends(metric_name)

        return insights
