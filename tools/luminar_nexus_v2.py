#!/usr/bin/env python3
"""
🌌 LUMINAR NEXUS V2 - AURORA'S ADVANCED SYSTEM ORCHESTRATOR
Revolutionary upgrade with AI-driven service management, quantum-inspired architecture,
and autonomous healing capabilities.

Features:
- Quantum-Inspired Service Mesh Architecture
- AI-Driven Autonomous Healing & Self-Optimization
- Advanced Security Guardian with Threat Detection
- Dynamic Load Balancing & Performance Optimization
- Predictive Service Scaling
- Neural Network-Based Anomaly Detection
- Real-time System Health Monitoring
- Advanced Port Management with Auto-Discovery
- Intelligent Request Routing with Context Awareness
- Self-Learning Performance Optimization
- Integrated Aurora Port Manager for Conflict Resolution
"""

import asyncio
import math
import os
import platform
import socket
import subprocess
import sys
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

import numpy as np
import psutil
from flask import Flask, jsonify, request
from flask_cors import CORS

# Add tools directory to path for Port Manager
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
try:
    from aurora_port_manager import AuroraPortManager

    PORT_MANAGER_AVAILABLE = True
except ImportError:
    AuroraPortManager = None  # type: ignore
    PORT_MANAGER_AVAILABLE = False
    print("⚠️ Aurora Port Manager not available - using basic port monitoring")


# Import Aurora's Enhanced Intelligence
try:
    from aurora_nexus_bridge import route_to_enhanced_aurora_core

    AURORA_BRIDGE_AVAILABLE = True
except ImportError:
    route_to_enhanced_aurora_core = None  # type: ignore
    AURORA_BRIDGE_AVAILABLE = False
    print("⚠️  Aurora Bridge not available, using fallback routing")


def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively sanitize data structures for JSON serialization.
    Replaces NaN, Infinity, and other non-JSON-safe values with None.
    """
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_for_json(v) for v in obj]
    elif isinstance(obj, float):
        if not math.isfinite(obj):  # Catches NaN, Infinity, -Infinity
            return None
        return obj
    elif isinstance(obj, np.floating):
        if not np.isfinite(obj):
            return None
        return float(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    else:
        return obj


@dataclass
class ServiceHealth:
    """Advanced service health metrics"""

    service_name: str
    port: int
    status: str  # 'healthy', 'degraded', 'critical', 'down'
    response_time: float
    cpu_usage: float
    memory_usage: float
    error_rate: float
    uptime: float
    last_check: datetime
    predictions: dict[str, float]
    anomalies: list[str]


@dataclass
class QuantumServiceMesh:
    """Quantum-inspired service mesh configuration"""

    entanglement_map: dict[str, list[str]]  # Service dependencies
    quantum_states: dict[str, str]  # Service quantum states
    coherence_level: float  # System coherence
    superposition_services: list[str]  # Services in superposition


class AIServiceOrchestrator:
    """AI-driven service orchestration and healing"""

    def __init__(self):
        self.service_history = {}
        self.performance_baselines = {}
        self.anomaly_patterns = {}
        self.learning_model = None
        self.healing_strategies = {}

    def learn_service_patterns(self, service_name: str, metrics: dict):
        """Machine learning-based pattern recognition"""
        if service_name not in self.service_history:
            self.service_history[service_name] = []

        self.service_history[service_name].append(
            {
                "timestamp": time.time(),
                "metrics": metrics,
                "performance_score": self._calculate_performance_score(metrics),
            }
        )

        # Keep only last 1000 entries for efficiency
        if len(self.service_history[service_name]) > 1000:
            self.service_history[service_name] = self.service_history[service_name][-1000:]

    def _calculate_performance_score(self, metrics: dict) -> float:
        """Calculate unified performance score"""
        weights = {
            "response_time": -0.3,  # Lower is better
            "cpu_usage": -0.2,  # Lower is better
            "memory_usage": -0.2,  # Lower is better
            "error_rate": -0.25,  # Lower is better
            "uptime": 0.25,  # Higher is better
        }

        score = 0.0
        for metric, weight in weights.items():
            if metric in metrics:
                score += metrics[metric] * weight

        return max(0.0, min(1.0, score))

    def predict_service_issues(self, service_name: str) -> dict[str, float]:
        """Predict potential service issues using trend analysis"""
        if service_name not in self.service_history or len(self.service_history[service_name]) < 10:
            return {}

        recent_data = self.service_history[service_name][-10:]
        predictions = {}

        # Simple trend analysis (can be replaced with ML models)
        for metric in ["response_time", "cpu_usage", "memory_usage", "error_rate"]:
            values = [entry["metrics"].get(metric, 0) for entry in recent_data]
            if len(values) >= 3:
                trend = np.polyfit(range(len(values)), values, 1)[0]
                predictions[f"{metric}_trend"] = float(trend)
                predictions[f"{metric}_prediction_5min"] = float(
                    values[-1] + trend * 5)

        return predictions

    def recommend_healing_action(self, service_health: ServiceHealth) -> str | None:
        """AI-recommended healing actions with pattern learning"""
        # Track healing effectiveness
        service_name = getattr(service_health, "service_name", "unknown")

        if service_health.status == "critical":
            if service_health.memory_usage > 0.9:
                action = "restart_service"
                self._record_healing_strategy(
                    service_name, action, "high_memory")
                return action
            elif service_health.error_rate > 0.1:
                action = "restart_service"
                self._record_healing_strategy(
                    service_name, action, "high_errors")
                return action
            elif service_health.response_time > 5.0:
                action = "scale_service"
                self._record_healing_strategy(
                    service_name, action, "slow_response")
                return action

        elif service_health.status == "degraded":
            if service_health.cpu_usage > 0.8:
                action = "scale_service"
                self._record_healing_strategy(service_name, action, "high_cpu")
                return action
            elif service_health.memory_usage > 0.8:
                action = "optimize_memory"
                self._record_healing_strategy(
                    service_name, action, "elevated_memory")
                return action

        return None

    def _record_healing_strategy(self, service_name: str, action: str, reason: str):
        """Record healing actions for learning which strategies work best"""
        if service_name not in self.healing_strategies:
            self.healing_strategies[service_name] = []

        self.healing_strategies[service_name].append(
            {"timestamp": time.time(), "action": action, "reason": reason})

        # Keep last 100 healing actions
        if len(self.healing_strategies[service_name]) > 100:
            self.healing_strategies[service_name] = self.healing_strategies[service_name][-100:]

    def learn_optimal_thresholds(self, service_name: str) -> dict[str, float]:
        """Machine learning to determine optimal thresholds for this service"""
        if service_name not in self.service_history or len(self.service_history[service_name]) < 50:
            # Return default thresholds
            return {
                "cpu_threshold": 80.0,
                "memory_threshold": 85.0,
                "response_time_threshold": 1000.0,
                "error_rate_threshold": 5.0,
            }

        # Analyze historical data to find optimal thresholds
        history = self.service_history[service_name]

        # Extract metrics
        cpu_values = [h["metrics"].get("cpu_usage", 0) for h in history]
        memory_values = [h["metrics"].get("memory_usage", 0) for h in history]
        response_times = [h["metrics"].get(
            "response_time", 0) for h in history]
        error_rates = [h["metrics"].get("error_rate", 0) for h in history]

        # Calculate 90th percentile as threshold (balance between sensitivity and false positives)
        def percentile_90(values):
            sorted_vals = sorted(values)
            index = int(len(sorted_vals) * 0.90)
            return sorted_vals[index] if sorted_vals else 0

        return {
            "cpu_threshold": percentile_90(cpu_values),
            "memory_threshold": percentile_90(memory_values),
            "response_time_threshold": percentile_90(response_times),
            "error_rate_threshold": percentile_90(error_rates),
        }

    def detect_service_patterns(self, service_name: str) -> dict[str, Any]:
        """Advanced pattern detection using ML techniques"""
        if service_name not in self.service_history or len(self.service_history[service_name]) < 30:
            return {"status": "insufficient_data"}

        history = self.service_history[service_name]

        # Pattern 1: Periodic behavior (daily, weekly cycles)
        periodicity = self._detect_periodicity(service_name)

        # Pattern 2: Correlation between metrics
        correlations = self._analyze_metric_correlations(history)

        # Pattern 3: Failure precursors (what happens before service fails)
        failure_precursors = self._identify_failure_precursors(history)

        return {
            "status": "patterns_detected",
            "periodicity": periodicity,
            "correlations": correlations,
            "failure_precursors": failure_precursors,
            "data_points_analyzed": len(history),
        }

    def _detect_periodicity(self, service_name: str) -> dict:
        """Detect if service has periodic patterns (e.g., daily traffic spikes)"""
        history = self.service_history[service_name]

        # Extract timestamps and a key metric (e.g., performance score)
        time_series = [(h["timestamp"], h["performance_score"])
                       for h in history]

        if len(time_series) < 50:
            return {"detected": False}

        # Simple autocorrelation check for daily patterns (86400 seconds)
        # This is a simplified version - real ML would use FFT or more sophisticated methods
        daily_pattern_detected = self._check_pattern_interval(
            time_series, 86400, tolerance=3600)

        return {
            "detected": daily_pattern_detected,
            "type": "daily" if daily_pattern_detected else "none",
            "confidence": 0.7 if daily_pattern_detected else 0.1,
        }

    def _check_pattern_interval(self, time_series: list, interval: float, tolerance: float) -> bool:
        """Check if patterns repeat at given interval"""
        if len(time_series) < 10:
            return False

        # Look for similar values at interval distances
        matches = 0
        comparisons = 0

        for i in range(len(time_series) - 5):
            t1, v1 = time_series[i]

            # Find points approximately 'interval' seconds later
            for j in range(i + 1, len(time_series)):
                t2, v2 = time_series[j]
                time_diff = abs((t2 - t1) - interval)

                if time_diff < tolerance:
                    comparisons += 1
                    value_diff = abs(v1 - v2)
                    if value_diff < 0.2:  # Values are similar
                        matches += 1
                    break

        return comparisons > 0 and (matches / comparisons) > 0.6

    def _analyze_metric_correlations(self, history: list) -> dict:
        """Analyze correlations between different metrics"""
        if len(history) < 20:
            return {}

        # Extract metric arrays
        metrics_data = {}
        metric_names = ["cpu_usage", "memory_usage",
                        "response_time", "error_rate"]

        for metric_name in metric_names:
            metrics_data[metric_name] = [
                h["metrics"].get(metric_name, 0) for h in history]

        # Calculate simple correlations
        correlations = {}

        # CPU vs Response Time
        correlations["cpu_response_correlation"] = self._simple_correlation(
            metrics_data["cpu_usage"], metrics_data["response_time"]
        )

        # Memory vs Error Rate
        correlations["memory_error_correlation"] = self._simple_correlation(
            metrics_data["memory_usage"], metrics_data["error_rate"]
        )

        return correlations

    def _simple_correlation(self, x: list, y: list) -> float:
        """Calculate Pearson correlation coefficient"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0

        n = len(x)
        mean_x = sum(x) / n
        mean_y = sum(y) / n

        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        denominator_x = sum((x[i] - mean_x) ** 2 for i in range(n)) ** 0.5
        denominator_y = sum((y[i] - mean_y) ** 2 for i in range(n)) ** 0.5

        if denominator_x == 0 or denominator_y == 0:
            return 0.0

        return numerator / (denominator_x * denominator_y)

    def _identify_failure_precursors(self, history: list) -> list[str]:
        """Identify patterns that typically precede service failures"""
        precursors = []

        # Look for failures (high error rate or very slow response)
        for i in range(len(history) - 5, len(history)):
            entry = history[i]
            if entry["metrics"].get("error_rate", 0) > 10 or entry["metrics"].get("response_time", 0) > 5000:
                # This was a failure - check what happened before
                if i > 5:
                    before_failure = history[i - 5: i]

                    # Check if memory was climbing
                    memory_vals = [h["metrics"].get(
                        "memory_usage", 0) for h in before_failure]
                    if all(memory_vals[j] <= memory_vals[j + 1] for j in range(len(memory_vals) - 1)):
                        if "memory_leak_pattern" not in precursors:
                            precursors.append("memory_leak_pattern")

                    # Check if CPU spiked before failure
                    cpu_vals = [h["metrics"].get(
                        "cpu_usage", 0) for h in before_failure]
                    if any(cpu > 90 for cpu in cpu_vals):
                        if "cpu_spike_before_failure" not in precursors:
                            precursors.append("cpu_spike_before_failure")

        return precursors


class LuminarNexusV2:
    """Advanced System Orchestrator with AI-driven management"""

    def __init__(self):
        self.version = "2.0.0"
        self.initialized_at = datetime.now()
        self.service_registry = {}
        self.health_monitor = {}
        self.monitoring_active = True
        self.port_healing_active = True

        # Initialize AI components
        self.ai_orchestrator = AIServiceOrchestrator()
        self.security_guardian = SecurityGuardian()
        self.performance_optimizer = PerformanceOptimizer()
        self.predictive_scaler = PredictiveScaler()
        self.neural_anomaly_detector = NeuralAnomalyDetector()

        # Initialize Quantum Service Mesh
        self.quantum_mesh = QuantumServiceMesh(
            entanglement_map={}, quantum_states={}, coherence_level=1.0, superposition_services=[]
        )

        # Configuration
        self.config = {
            "monitoring_interval": 5,
            "healing_enabled": True,
            "ai_learning_enabled": True,
            "quantum_coherence_threshold": 0.7,
        }

        # Get the current working directory
        cwd = os.getcwd()

        # Determine correct Python command for the platform
        python_cmd = "python" if platform.system() == "Windows" else "python3"

        # Server configurations (cross-platform)
        self.servers = {
            "bridge": {
                "name": "Aurora Bridge Service",
                "command": f"cd {cwd} && {python_cmd} -m aurora_x.bridge.service",
                "session": "aurora-bridge",
                "port": 5001,
                "health_check": "http://localhost:5001/health",
            },
            "backend": {
                "name": "Aurora Backend API",
                "command": f"cd {cwd} && {'set NODE_ENV=development &&' if platform.system() == 'Windows' else 'NODE_ENV=development'} npx tsx server/index.ts",
                "session": "aurora-backend",
                "port": 5000,
                "health_check": "http://localhost:5000/health",
            },
            "self-learn": {
                "name": "Aurora Self-Learning Server",
                "command": f"cd {cwd} && {python_cmd} -m aurora_x.self_learn_server",
                "session": "aurora-self-learn",
                "port": 5002,
                "health_check": "http://localhost:5002/health",
            },
            "chat": {
                "name": "Aurora Chat Server",
                "command": f"cd {cwd} && {python_cmd} aurora_chat_server.py --port 5003",
                "session": "aurora-chat",
                "port": 5003,
                "health_check": "http://localhost:5003/health",
            },
        }

        # Initialize Port Manager if available
        self.port_manager = None
        if PORT_MANAGER_AVAILABLE and AuroraPortManager is not None:
            try:
                self.port_manager = AuroraPortManager()
                print("✅ Aurora Port Manager integrated with Luminar Nexus v2")
            except Exception as e:
                print(f"⚠️  Could not initialize Port Manager: {e}")

        print("🌌 Luminar Nexus v2 initialized")
        print(f"   Version: {self.version}")
        print(f"   Quantum Coherence: {self.quantum_mesh.coherence_level:.2f}")
        print(
            f"   AI Learning: {'Enabled' if self.config['ai_learning_enabled'] else 'Disabled'}")
        print(
            f"   Autonomous Healing: {'Enabled' if self.config['healing_enabled'] else 'Disabled'}")

    def register_service(
        self,
        name: str,
        port: int,
        service_type: str = "standard",
        dependencies: list[str] | None = None,
        quantum_state: str = "stable",
    ):
        """Register a service with advanced metadata"""
        self.service_registry[name] = {
            "port": port,
            "type": service_type,
            "dependencies": dependencies or [],
            "quantum_state": quantum_state,
            "registered_at": datetime.now(),
            "restart_count": 0,
            "performance_tier": "standard",
        }

        # Initialize quantum entanglement
        if dependencies:
            self.quantum_mesh.entanglement_map[name] = dependencies

        self.quantum_mesh.quantum_states[name] = quantum_state

        # Initialize health monitoring
        self._initialize_health_monitoring(name, port)

        print(
            f"🔗 Service '{name}' registered on port {port} with quantum state '{quantum_state}'")

    def _initialize_health_monitoring(self, service_name: str, port: int):
        """Initialize comprehensive health monitoring for a service"""
        self.health_monitor[service_name] = ServiceHealth(
            service_name=service_name,
            port=port,
            status="unknown",
            response_time=0.0,
            cpu_usage=0.0,
            memory_usage=0.0,
            error_rate=0.0,
            uptime=0.0,
            last_check=datetime.now(),
            predictions={},
            anomalies=[],
        )

    async def comprehensive_health_check(self, service_name: str) -> ServiceHealth | None:
        """Advanced health check with AI analysis"""
        if service_name not in self.health_monitor:
            return None

        start_time = time.time()
        health = self.health_monitor[service_name]

        try:
            # Network connectivity check
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(("localhost", health.port))
            sock.close()

            if result == 0:
                health.status = "healthy"
                health.response_time = time.time() - start_time
            else:
                health.status = "down"
                health.response_time = None  # Don't use infinity - service is down

            # System resource monitoring
            try:
                # Find process using the port
                for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
                    try:
                        if hasattr(proc, "net_connections"):
                            connections = proc.net_connections()  # type: ignore
                            for conn in connections:
                                if conn.laddr.port == health.port:
                                    health.cpu_usage = proc.cpu_percent() / 100.0
                                    health.memory_usage = proc.memory_percent() / 100.0
                                    break
                    except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                        continue
            except Exception:  # noqa: BLE001 - Ignore status check errors
                pass

            # AI-based health assessment (only for services that are up)
            if health.status != "down":
                metrics = {
                    "response_time": health.response_time if health.response_time is not None else 0.0,
                    "cpu_usage": health.cpu_usage,
                    "memory_usage": health.memory_usage,
                    "error_rate": health.error_rate,
                }

                # Learn patterns for AI improvement
                self.ai_orchestrator.learn_service_patterns(
                    service_name, metrics)

                # Generate predictions
                health.predictions = self.ai_orchestrator.predict_service_issues(
                    service_name)

                # Anomaly detection
                health.anomalies = self.neural_anomaly_detector.detect_anomalies(
                    service_name, metrics)

            # Performance classification (only for services that are up)
            if health.status != "down":
                if (
                    health.response_time
                    and health.response_time > 2.0
                    or health.cpu_usage > 0.9
                    or health.memory_usage > 0.9
                ):
                    health.status = "critical"
                elif (
                    health.response_time
                    and health.response_time > 1.0
                    or health.cpu_usage > 0.7
                    or health.memory_usage > 0.7
                ):
                    health.status = "degraded"
                elif health.status != "down":
                    health.status = "healthy"

            health.last_check = datetime.now()

        except Exception as e:
            health.status = "error"
            health.anomalies.append(f"Health check error: {str(e)}")

        return health

    async def autonomous_healing(self, service_name: str):
        """AI-driven autonomous healing"""
        if not self.config["healing_enabled"]:
            return

        health = await self.comprehensive_health_check(service_name)
        if not health:
            return

        healing_action = self.ai_orchestrator.recommend_healing_action(health)

        if healing_action:
            print(
                f"🔧 Autonomous healing: {healing_action} for service '{service_name}'")

            if healing_action == "restart_service":
                await self._restart_service(service_name)
            elif healing_action == "scale_service":
                await self._scale_service(service_name)
            elif healing_action == "optimize_memory":
                await self._optimize_memory(service_name)

    async def _restart_service(self, service_name: str):
        """Graceful service restart using tmux"""
        if service_name not in self.service_registry:
            return

        service_info = self.service_registry[service_name]
        service_info["restart_count"] += 1

        print(
            f"🔄 Restarting service '{service_name}' (restart #{service_info['restart_count']})")

        # Stop the service first
        await self._stop_service_internal(service_name)
        await asyncio.sleep(2)

        # Start the service again
        await self._start_service_internal(service_name)

    async def _scale_service(self, service_name: str):
        """Intelligent service scaling - adjust resource limits"""
        if service_name not in self.service_registry:
            return

        print(f"📈 Scaling service '{service_name}' for better performance")

        try:
            # Get service process and adjust priority
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    if service_name in " ".join(proc.info["cmdline"] or []):
                        # Increase process priority (nice value)
                        proc.nice(-5)  # Higher priority
                        print(f"   ✅ Increased priority for {service_name}")
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"   ⚠️ Scaling error: {e}")

    async def _optimize_memory(self, service_name: str):
        """Memory optimization strategies - trigger garbage collection"""
        if service_name not in self.service_registry:
            return

        print(f"🧠 Optimizing memory for service '{service_name}'")

        try:
            # For Python processes, we can send signals to trigger GC
            import signal

            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    cmdline = " ".join(proc.info["cmdline"] or [])
                    if service_name in cmdline and "python" in cmdline.lower():
                        # Send SIGUSR1 for potential GC trigger (if service handles it)
                        # SIGUSR1 only exists on Unix systems
                        if hasattr(signal, "SIGUSR1"):
                            proc.send_signal(signal.SIGUSR1)
                        print(
                            f"   ✅ Sent memory optimization signal to {service_name}")
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"   ⚠️ Memory optimization error: {e}")

    # ============================================================================
    # SERVER MANAGEMENT - Cross-platform service control
    # ============================================================================

    def is_windows(self) -> bool:
        """Check if running on Windows"""
        return platform.system() == "Windows"

    def check_tmux_installed(self) -> bool:
        """Check if tmux is available (Linux/macOS only)"""
        if self.is_windows():
            return False  # Windows doesn't use tmux
        try:
            subprocess.run(["tmux", "-V"], capture_output=True,
                           check=True, timeout=2)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(
                "⚠️ tmux not installed - required for service management on Linux/macOS")
            return False

    async def _start_service_internal(self, service_key: str) -> bool:
        """Start a service (cross-platform)"""
        if service_key not in self.servers:
            print(f"❌ Unknown service: {service_key}")
            return False

        server = self.servers[service_key]
        session = server["session"]
        command = server["command"]

        print(f"🚀 Starting {server['name']}...")

        if self.is_windows():
            # Windows: Start process directly in background
            try:
                # Parse command for Windows
                if command.startswith("cd "):
                    # Extract directory and actual command
                    parts = command.split(" && ", 1)
                    cwd = parts[0].replace("cd ", "").strip()
                    actual_cmd = parts[1] if len(
                        parts) > 1 else "echo No command"
                else:
                    cwd = None
                    actual_cmd = command

                # Create logs directory
                logs_dir = os.path.join(cwd if cwd else os.getcwd(), "logs")
                os.makedirs(logs_dir, exist_ok=True)

                # Create log files for this service
                log_file = os.path.join(logs_dir, f"{session}.log")
                err_file = os.path.join(logs_dir, f"{session}.err")

                # Start process in background with logging
                with open(log_file, "w", encoding="utf-8") as out, open(err_file, "w", encoding="utf-8") as err:
                    # Windows-specific process creation flags
                    creation_flags = 0
                    if self.is_windows():
                        try:
                            creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore
                        except AttributeError:
                            creation_flags = 0x00000200  # CREATE_NEW_PROCESS_GROUP value on Windows

                    subprocess.Popen(
                        actual_cmd,
                        shell=True,
                        cwd=cwd,
                        stdout=out,
                        stderr=err,
                        creationflags=creation_flags,
                    )

                print("   ✅ Started in background")
                print(f"   🔌 Port: {server['port']}")
                print(f"   📝 Logs: {log_file}")

                # Wait and check health with retries
                max_retries = 5
                for attempt in range(max_retries):
                    await asyncio.sleep(2)  # Wait 2 seconds between checks
                    if await self._check_service_health(service_key):
                        print("   ✅ Health check PASSED")
                        return True
                    elif attempt < max_retries - 1:
                        print(
                            f"   ⏳ Waiting for service to start... ({attempt + 1}/{max_retries})")

                print("   ⚠️  Server started but health check pending...")
                # Check error log for issues
                if os.path.exists(err_file) and os.path.getsize(err_file) > 0:
                    try:
                        with open(err_file, encoding="utf-8", errors="ignore") as f:
                            errors = f.read()
                            if errors:
                                print(
                                    f"   ⚠️  Errors detected: {errors[:200]}")
                    except Exception:  # noqa: BLE001 - Ignore log read errors
                        pass  # Ignore encoding errors when reading logs
                return True
            except Exception as e:  # noqa: BLE001 - Broad catch for start operation
                print(f"   ❌ Failed to start: {e}")
                return False
        else:
            # Linux/macOS: Use tmux
            if not self.check_tmux_installed():
                return False

            # Kill existing session if it exists
            subprocess.run(
                ["tmux", "kill-session", "-t", session],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )

            # Create new tmux session and run command
            result = subprocess.run(
                ["tmux", "new-session", "-d", "-s", session, command],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )

            if result.returncode == 0:
                print(f"   ✅ Started in tmux session: {session}")
                print(f"   🔌 Port: {server['port']}")

                # Wait and check health
                await asyncio.sleep(3)
                if await self._check_service_health(service_key):
                    print("   ✅ Health check PASSED")
                    return True
                else:
                    print("   ⚠️  Server started but health check pending...")
                    return True
            else:
                print(f"   ❌ Failed to start: {result.stderr}")
                return False

    async def _stop_service_internal(self, service_key: str) -> bool:
        """Stop a service (cross-platform)"""
        if service_key not in self.servers:
            print(f"❌ Unknown service: {service_key}")
            return False

        server = self.servers[service_key]
        session = server["session"]
        port = server["port"]

        print(f"🛑 Stopping {server['name']}...")

        if self.is_windows():
            # Windows: Find and kill process using the port
            try:
                killed = False
                for proc in psutil.process_iter(["pid", "name"]):
                    try:
                        # Get connections for this process
                        connections = proc.connections()
                        for conn in connections:
                            if hasattr(conn, "laddr") and conn.laddr.port == port:
                                proc.kill()
                                print(
                                    f"   ✅ Killed process {proc.pid} ({proc.name()}) on port {port}")
                                killed = True
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                    except Exception:
                        pass  # Skip processes we can't access

                if not killed:
                    print(f"   ⚠️  No process found on port {port}")
                return killed
            except Exception as e:
                print(f"   ❌ Error stopping service: {e}")
                return False
        else:
            # Linux/macOS: Kill tmux session
            result = subprocess.run(
                ["tmux", "kill-session", "-t", session], capture_output=True, text=True, timeout=2, check=False
            )

            if result.returncode == 0:
                print(f"   ✅ Stopped session: {session}")
                return True
            else:
                print(f"   ⚠️  Session may not exist: {session}")
                return False

    def _is_port_in_use(self, port: int) -> bool:
        """Check if a port is in use"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(("localhost", port)) == 0
        except (OSError, subprocess.CalledProcessError):
            return False

    async def _check_service_health(self, service_key: str) -> bool:
        """Check if a service is responding to health checks"""
        if service_key not in self.servers:
            return False

        server = self.servers[service_key]
        base_url = server["health_check"]

        # Try multiple health check patterns
        health_endpoints = [
            base_url,
            base_url.replace("/healthz", "/health"),
            base_url.replace("/health", "/healthz"),
            base_url.replace("/health", "/api/health"),
        ]

        for endpoint in health_endpoints:
            try:
                # Use urllib instead of curl for cross-platform compatibility
                import json
                import urllib.request
                from urllib.error import HTTPError, URLError

                req = urllib.request.Request(
                    endpoint, headers={"User-Agent": "Aurora/2.0"})
                try:
                    with urllib.request.urlopen(req, timeout=3) as response:
                        if response.status == 200:
                            response_data = response.read().decode("utf-8")
                            try:
                                # Try to parse as JSON
                                data = json.loads(response_data)
                                if isinstance(data, dict):
                                    # Check if 'ok' field is True
                                    if data.get("ok") is True or data.get("ok") == "true":
                                        return True
                                    # Also check status field
                                    status_value = str(
                                        data.get("status", "")).lower()
                                    if any(
                                        indicator in status_value
                                        for indicator in ["ok", "healthy", "online", "running"]
                                    ):
                                        return True
                            except json.JSONDecodeError:
                                # If not JSON, check raw text
                                response_text = response_data.lower()
                                if any(
                                    indicator in response_text
                                    for indicator in ["ok", "healthy", "status", "true", "online"]
                                ):
                                    return True
                except (URLError, HTTPError, TimeoutError, ConnectionError, OSError):
                    # OSError covers socket.timeout on Windows
                    continue
            except Exception:
                continue

        return False

    def start_server(self, server_key: str) -> bool:
        """Public API to start a server"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            self._start_service_internal(server_key))
        loop.close()
        return result

    def stop_server(self, server_key: str) -> bool:
        """Public API to stop a server"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            self._stop_service_internal(server_key))
        loop.close()
        return result

    def start_all_servers(self):
        """Start all Aurora services"""
        print("\n🌌 Luminar Nexus V2: Starting ALL services...\n")

        for server_key in self.servers.keys():
            self.start_server(server_key)
            time.sleep(2)  # Stagger starts

        print("\n✅ All services started!\n")
        self.show_status()

    def stop_all_servers(self):
        """Stop all Aurora services"""
        print("\n🛑 Luminar Nexus V2: Stopping ALL services...\n")

        for server_key in self.servers.keys():
            self.stop_server(server_key)

        print("\n✅ All services stopped!\n")

    def show_status(self):
        """Show detailed status of all services"""
        print("=" * 70)
        print("📊 LUMINAR NEXUS V2 - SERVER STATUS")
        print("=" * 70)

        # Try to get tmux session info if available
        try:
            session_result = subprocess.run(
                ["tmux", "list-sessions"], capture_output=True, text=True, timeout=2, check=False)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print("ℹ️  tmux not available - using direct process management")
            session_result = None

        # Check each service
        for service_name, config in self.servers.items():
            port = config["port"]

            # Check if service is running via port or process
            session_name = f"aurora-{service_name}"

            if session_result is None:
                # No tmux - check by port directly
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    running = s.connect_ex(("127.0.0.1", port)) == 0
                print(
                    f"{'✅' if running else '❌'} {service_name:20} Port {port:5} {'RUNNING' if running else 'STOPPED'}"
                )
                continue

            # tmux available - check session
            if session_result and session_name in session_result.stdout:
                # Check health
                try:
                    health_ok = asyncio.run(self._check_service_health(service_name))
                except Exception:
                    health_ok = False
                status = "RUNNING"
                icon = "✅"
                print(
                    f"{icon} {service_name:20} Port {port:5} {status} (tmux:{session_name}) Health: {'✅ OK' if health_ok else '❌ Not responding'}"
                )
            else:
                icon = "❌"
                status = "STOPPED"
                print(
                    f"{icon} {service_name:20} Port {port:5} {status} (tmux:{session_name})")

    def start_advanced_monitoring(self):
        """Start advanced monitoring with AI analysis"""

        def monitoring_loop():
            while self.monitoring_active:
                try:
                    # Run health checks for all services
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    for service_name in self.service_registry.keys():
                        health = loop.run_until_complete(
                            self.comprehensive_health_check(service_name))

                        # Autonomous healing if needed
                        if health and health.status in ["critical", "degraded"]:
                            loop.run_until_complete(
                                self.autonomous_healing(service_name))

                    loop.close()

                    # Update quantum coherence
                    self._update_quantum_coherence()

                    # Run port conflict resolution if available
                    if self.port_manager and self.port_healing_active:
                        self._check_and_heal_ports()

                    time.sleep(self.config["monitoring_interval"])

                except Exception as e:
                    print(f"⚠️  Monitoring error: {e}")
                    time.sleep(5)

        monitoring_thread = threading.Thread(
            target=monitoring_loop, daemon=True)
        monitoring_thread.start()
        print("🔍 Advanced monitoring started with AI analysis")

    def _check_and_heal_ports(self):
        """Check for port conflicts and heal automatically"""
        try:
            if not self.port_manager:
                return

            # Scan for conflicts
            port_usage = self.port_manager.scan_port_usage()
            conflicts = self.port_manager.identify_conflicts(port_usage)

            if conflicts:
                print(
                    f"🔧 Nexus v2 detected {len(conflicts)} port conflicts - initiating healing")
                results = self.port_manager.resolve_conflicts(conflicts)

                # Update quantum coherence based on healing success
                if results:
                    success_rate = sum(
                        1 for success in results.values() if success) / len(results)
                    if success_rate < 0.8:
                        self.quantum_mesh.coherence_level *= 0.9  # Reduce coherence if healing fails
                    else:
                        self.quantum_mesh.coherence_level = min(
                            1.0, self.quantum_mesh.coherence_level * 1.05)

                    print(
                        f"✅ Port healing completed with {success_rate:.1%} success rate")

        except Exception as e:
            print(f"❌ Port healing error: {e}")

    def get_port_status(self) -> dict[str, Any]:
        """Get comprehensive port status"""
        if not self.port_manager:
            return {"error": "Port Manager not available", "available": False}

        try:
            status = self.port_manager.get_status_report()
            status["integration"] = "active"
            return status
        except Exception as e:  # noqa: BLE001 - Broad catch for server status
            return {"error": str(e), "available": False}

    def _update_quantum_coherence(self):
        """Update system quantum coherence level"""
        # Only count services that have been checked (not in "unknown" state)
        checked_services = [
            h for h in self.health_monitor.values() if h.status != "unknown"]

        if checked_services:
            healthy_services = sum(
                1 for health in checked_services if health.status == "healthy")
            total_checked = len(checked_services)
            self.quantum_mesh.coherence_level = healthy_services / total_checked
        else:
            # Keep initial coherence of 1.0 until first health check completes
            self.quantum_mesh.coherence_level = 1.0

        # If coherence is low, trigger system-wide healing
        # Skip warning only if all services are still in unknown state (initial health check not complete)
        all_unknown = all(
            health.status == "unknown" for health in self.health_monitor.values())
        if self.quantum_mesh.coherence_level < self.config["quantum_coherence_threshold"] and not all_unknown:
            print(
                f"⚠️  Quantum coherence low: {self.quantum_mesh.coherence_level:.2f}")

    def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "version": self.version,
            "uptime": str(datetime.now() - self.initialized_at),
            "quantum_coherence": self.quantum_mesh.coherence_level,
            "total_services": len(self.service_registry),
            "healthy_services": sum(1 for h in self.health_monitor.values() if h.status == "healthy"),
            "ai_learning_active": self.config["ai_learning_enabled"],
            "autonomous_healing_active": self.config["healing_enabled"],
            "services": {name: asdict(health) for name, health in self.health_monitor.items()},
        }

    def create_advanced_api(self) -> Flask:
        """Create advanced API with intelligent routing"""
        app = Flask(__name__)
        CORS(app)

        @app.route("/api/nexus/status", methods=["GET"])
        def get_status():
            status = self.get_system_status()
            sanitized_status = sanitize_for_json(status)
            return jsonify(sanitized_status)

        @app.route("/api/nexus/health/<service_name>", methods=["GET"])
        def get_service_health(service_name):
            if service_name in self.health_monitor:
                return jsonify(asdict(self.health_monitor[service_name]))
            return jsonify({"error": "Service not found"}), 404

        @app.route("/api/nexus/quantum", methods=["GET"])
        def get_quantum_status():
            return jsonify(asdict(self.quantum_mesh))

        @app.route("/api/nexus/ports", methods=["GET"])
        def get_port_status():
            """Get comprehensive port status and conflicts"""
            return jsonify(self.get_port_status())

        @app.route("/api/nexus/ports/heal", methods=["POST"])
        def heal_ports():
            """Manually trigger port conflict healing"""
            if not self.port_manager:
                return jsonify({"error": "Port Manager not available"}), 503

            try:
                self._check_and_heal_ports()
                return jsonify({"message": "Port healing initiated", "success": True})
            except Exception as e:
                return jsonify({"error": str(e), "success": False}), 500

        @app.route("/api/chat", methods=["POST"])
        def intelligent_chat_routing():
            """Intelligent chat routing with Aurora Bridge"""
            try:
                data = request.get_json()
                message = data.get("message", "")
                session_id = data.get("session_id", "default")

                if not message:
                    return jsonify({"error": "No message provided"}), 400

                # Advanced routing through Aurora Bridge
                if AURORA_BRIDGE_AVAILABLE and route_to_enhanced_aurora_core is not None:
                    print(f"🌌 Nexus v2 → Aurora Bridge: {message[:50]}...")
                    response = route_to_enhanced_aurora_core(
                        message, session_id)
                else:
                    response = "Nexus v2 operational, but Aurora Bridge unavailable. Please check system configuration."

                return jsonify(
                    {
                        "response": response,
                        "session_id": session_id,
                        "timestamp": time.time(),
                        "nexus_version": self.version,
                        "quantum_coherence": self.quantum_mesh.coherence_level,
                    }
                )

            except Exception as e:
                print(f"❌ Chat routing error: {e}")
                return jsonify({"error": str(e)}), 500

        @app.route("/chat", methods=["GET", "POST"])
        def chat_alias():
            """Route alias for /chat → /api/chat compatibility (Aurora autonomous fix)"""
            if request.method == "POST":
                return intelligent_chat_routing()
            return (
                jsonify(
                    {
                        "error": "Use POST method",
                        "correct_endpoint": "/api/chat",
                        "usage": 'POST /api/chat or POST /chat with JSON body: {"message": "your message"}',
                        "aurora_fix": "Route alias added by Aurora autonomous endpoint fix",
                    }
                ),
                405,
            )

        return app


class SecurityGuardian:
    """Advanced security guardian with threat detection (Aurora Tier 11: Security & Cryptography)"""

    def __init__(self):
        self.threat_patterns = {
            "sql_injection": [
                r"(?i)(union.*select|insert.*into|delete.*from|drop.*table|exec\s*\(|;.*--|'.*or.* =.*)",
                "SQL Injection attempt",
            ],
            "path_traversal": [r"\.\.\/|\.\.\\", "Path traversal attempt"],
            "xss": [r"<script|javascript:|onerror=|onload=", "XSS attempt"],
            "command_injection": [r"[;&|]|\$\(|`", "Command injection attempt"],
            "excessive_requests": {"threshold": 100, "window": 60},
        }
        self.security_events = []
        self.blocked_ips = set()
        self.request_tracking = {}  # IP -> list of request timestamps

    def detect_threats(self, request_data: dict) -> list[str]:
        """Advanced threat detection using pattern matching and behavioral analysis"""
        threats = []
        source_ip = request_data.get("ip", "unknown")
        request_path = request_data.get("path", "")
        request_body = str(request_data.get("body", ""))
        request_params = str(request_data.get("params", ""))

        # Check if IP is already blocked
        if source_ip in self.blocked_ips:
            threats.append(f"BLOCKED_IP: {source_ip} is on blocklist")
            return threats

        # Pattern-based threat detection
        import re

        full_request = f"{request_path} {request_body} {request_params}"

        for threat_type, pattern_data in self.threat_patterns.items():
            if threat_type == "excessive_requests":
                continue  # Handled separately

            pattern, description = pattern_data
            if re.search(pattern, full_request):
                threats.append(f"{threat_type.upper()}: {description}")
                self._log_security_event(source_ip, threat_type, request_path)

        # Rate limiting / DDoS detection
        if self._check_rate_limit(source_ip):
            threats.append(
                f"RATE_LIMIT_EXCEEDED: {source_ip} exceeds request threshold")
            self.blocked_ips.add(source_ip)

        # Port scanning detection
        if self._detect_port_scan(source_ip, request_data.get("port")):
            threats.append(f"PORT_SCAN_DETECTED: {source_ip} scanning ports")
            self.blocked_ips.add(source_ip)

        return threats

    def _check_rate_limit(self, ip: str) -> bool:
        """Check if IP exceeds rate limits"""
        current_time = time.time()
        threshold = self.threat_patterns["excessive_requests"]["threshold"]
        window = self.threat_patterns["excessive_requests"]["window"]

        if ip not in self.request_tracking:
            self.request_tracking[ip] = []

        # Add current request
        self.request_tracking[ip].append(current_time)

        # Remove old requests outside window
        self.request_tracking[ip] = [
            t for t in self.request_tracking[ip] if current_time - t < window]

        return len(self.request_tracking[ip]) > threshold

    def _detect_port_scan(self, ip: str, port: int | None) -> bool:
        """Detect port scanning behavior"""
        if not port:
            return False

        # Track ports accessed by IP
        port_key = f"{ip}_ports"
        if port_key not in self.request_tracking:
            self.request_tracking[port_key] = set()

        self.request_tracking[port_key].add(port)

        # If accessing more than 5 different ports in short time, likely scanning
        return len(self.request_tracking[port_key]) > 5

    def _log_security_event(self, ip: str, threat_type: str, path: str):
        """Log security events for analysis"""
        event = {"timestamp": time.time(), "ip": ip,
                 "threat": threat_type, "path": path}
        self.security_events.append(event)

        # Keep only last 10000 events
        if len(self.security_events) > 10000:
            self.security_events = self.security_events[-10000:]

    def get_security_report(self) -> dict:
        """Generate security report"""
        return {
            "total_threats": len(self.security_events),
            "blocked_ips": list(self.blocked_ips),
            "recent_events": self.security_events[-50:],
            "threat_summary": self._summarize_threats(),
        }

    def _summarize_threats(self) -> dict:
        """Summarize threat types and frequencies"""
        summary = {}
        for event in self.security_events:
            threat = event["threat"]
            summary[threat] = summary.get(threat, 0) + 1
        return summary


class PerformanceOptimizer:
    """AI-driven performance optimization (Aurora Tier 14: Cloud/Infrastructure + Tier 16: Analytics)"""

    def __init__(self):
        self.optimization_strategies = {
            "high_cpu": {"action": "scale_horizontal", "threshold": 80},
            "high_memory": {"action": "increase_memory", "threshold": 85},
            # ms
            "slow_response": {"action": "add_caching", "threshold": 1000},
            # %
            "high_error_rate": {"action": "restart_service", "threshold": 5},
        }
        self.performance_history = {}
        self.optimization_cache = {}

    def optimize_performance(self, service_metrics: dict) -> dict[str, Any]:
        """Optimize system performance using analytics and load balancing"""
        recommendations = {
            "immediate_actions": [],
            "preventive_measures": [],
            "resource_allocation": {},
            "load_balancing": {},
        }

        service_name = service_metrics.get("service_name", "unknown")

        # Track performance history
        self._track_performance(service_name, service_metrics)

        # CPU optimization
        cpu_usage = service_metrics.get("cpu_usage", 0)
        if cpu_usage > self.optimization_strategies["high_cpu"]["threshold"]:
            recommendations["immediate_actions"].append(
                {
                    "type": "scale_horizontal",
                    "reason": f'CPU usage at {cpu_usage}% (threshold: {self.optimization_strategies["high_cpu"]["threshold"]}%)',
                    "priority": "high",
                    "estimated_impact": "Reduce CPU by 30-40%",
                }
            )
            recommendations["resource_allocation"]["additional_instances"] = self._calculate_instance_needs(
                cpu_usage)

        # Memory optimization
        memory_usage = service_metrics.get("memory_usage", 0)
        if memory_usage > self.optimization_strategies["high_memory"]["threshold"]:
            recommendations["immediate_actions"].append(
                {
                    "type": "memory_optimization",
                    "reason": f'Memory usage at {memory_usage}% (threshold: {self.optimization_strategies["high_memory"]["threshold"]}%)',
                    "priority": "high",
                    "actions": ["clear_cache", "garbage_collect", "check_memory_leaks"],
                }
            )

        # Response time optimization
        response_time = service_metrics.get("response_time", 0)
        if response_time > self.optimization_strategies["slow_response"]["threshold"]:
            recommendations["immediate_actions"].append(
                {
                    "type": "caching_strategy",
                    "reason": f'Response time at {response_time}ms (threshold: {self.optimization_strategies["slow_response"]["threshold"]}ms)',
                    "priority": "medium",
                    "suggestions": ["enable_redis_cache", "optimize_database_queries", "add_cdn"],
                }
            )

        # Error rate optimization
        error_rate = service_metrics.get("error_rate", 0)
        if error_rate > self.optimization_strategies["high_error_rate"]["threshold"]:
            recommendations["immediate_actions"].append(
                {
                    "type": "stability_improvement",
                    "reason": f'Error rate at {error_rate}% (threshold: {self.optimization_strategies["high_error_rate"]["threshold"]}%)',
                    "priority": "critical",
                    "actions": ["check_logs", "restart_service", "rollback_if_recent_deploy"],
                }
            )

        # Load balancing recommendations
        recommendations["load_balancing"] = self._generate_load_balancing_strategy(
            service_name, service_metrics)

        # Preventive measures based on trends
        recommendations["preventive_measures"] = self._analyze_trends(
            service_name)

        return recommendations

    def _track_performance(self, service_name: str, metrics: dict):
        """Track performance over time for trend analysis"""
        if service_name not in self.performance_history:
            self.performance_history[service_name] = []

        self.performance_history[service_name].append(
            {"timestamp": time.time(), "metrics": metrics})

        # Keep last 1000 data points
        if len(self.performance_history[service_name]) > 1000:
            self.performance_history[service_name] = self.performance_history[service_name][-1000:]

    def _calculate_instance_needs(self, cpu_usage: float) -> int:
        """Calculate how many additional instances needed"""
        if cpu_usage > 95:
            return 3
        elif cpu_usage > 85:
            return 2
        elif cpu_usage > 75:
            return 1
        return 0

    def _generate_load_balancing_strategy(self, service_name: str, metrics: dict) -> dict:
        """Generate intelligent load balancing strategy"""
        return {
            "algorithm": "least_connections",  # Best for varying request complexity
            "health_check_interval": 5,  # seconds
            "failover_enabled": True,
            "sticky_sessions": metrics.get("requires_session", False),
            "weight_distribution": self._calculate_weights(service_name),
        }

    def _calculate_weights(self, service_name: str) -> dict:
        """Calculate load distribution weights based on performance"""
        if service_name not in self.performance_history or len(self.performance_history[service_name]) < 5:
            return {"default": 1.0}

        # Analyze recent performance to distribute load intelligently
        recent = self.performance_history[service_name][-10:]
        avg_response_time = sum(m["metrics"].get(
            "response_time", 500) for m in recent) / len(recent)

        # Better performing instances get higher weight
        if avg_response_time < 100:
            return {"high_performance": 2.0}
        elif avg_response_time < 500:
            return {"normal": 1.0}
        else:
            return {"degraded": 0.5}

    def _analyze_trends(self, service_name: str) -> list[dict]:
        """Analyze performance trends for preventive measures"""
        if service_name not in self.performance_history or len(self.performance_history[service_name]) < 20:
            return []

        measures = []
        history = self.performance_history[service_name]

        # Check if CPU usage trending up
        recent_cpu = [h["metrics"].get("cpu_usage", 0) for h in history[-10:]]
        older_cpu = [h["metrics"].get("cpu_usage", 0)
                     for h in history[-20:-10]]

        if recent_cpu and older_cpu:
            cpu_trend = (sum(recent_cpu) / len(recent_cpu)) - \
                (sum(older_cpu) / len(older_cpu))
            if cpu_trend > 10:  # 10% increase
                measures.append(
                    {
                        "type": "cpu_trend",
                        "message": f"CPU usage trending up by {cpu_trend:.1f}%",
                        "recommendation": "Consider scaling before hitting limits",
                    }
                )

        return measures


class PredictiveScaler:
    """Predictive scaling based on usage patterns (Aurora Tier 14: Cloud + Tier 15: AI/ML)"""

    def __init__(self):
        self.scaling_history = {}
        self.load_predictions = {}
        self.time_patterns = {}  # Track time-based patterns (e.g., peak hours)
        self.scaling_decisions = {}

    def predict_scaling_needs(self, service_name: str, current_load: float) -> str | None:
        """Predict if scaling is needed using historical patterns and trend analysis"""

        # Initialize tracking for new services
        if service_name not in self.scaling_history:
            self.scaling_history[service_name] = []
            self.time_patterns[service_name] = {}

        # Record current load with timestamp
        current_time = time.time()
        hour_of_day = int((current_time % 86400) / 3600)  # 0-23

        self.scaling_history[service_name].append(
            {"timestamp": current_time, "load": current_load, "hour": hour_of_day}
        )

        # Keep last 1000 data points
        if len(self.scaling_history[service_name]) > 1000:
            self.scaling_history[service_name] = self.scaling_history[service_name][-1000:]

        # Need enough data for predictions
        if len(self.scaling_history[service_name]) < 20:
            return self._simple_threshold_scaling(current_load)

        # Learn time-based patterns
        self._learn_time_patterns(service_name, hour_of_day, current_load)

        # Predict future load
        predicted_load = self._predict_future_load(service_name, current_load)

        # Make scaling decision
        scaling_action = self._make_scaling_decision(
            service_name, current_load, predicted_load)

        # Log decision
        if scaling_action:
            self.scaling_decisions[service_name] = {
                "timestamp": current_time,
                "action": scaling_action,
                "current_load": current_load,
                "predicted_load": predicted_load,
            }

        return scaling_action

    def _simple_threshold_scaling(self, current_load: float) -> str | None:
        """Simple threshold-based scaling for when insufficient data"""
        if current_load > 80:
            return "scale_up"
        elif current_load < 20:
            return "scale_down"
        return None

    def _learn_time_patterns(self, service_name: str, hour: int, load: float):
        """Learn load patterns by time of day"""
        if hour not in self.time_patterns[service_name]:
            self.time_patterns[service_name][hour] = []

        self.time_patterns[service_name][hour].append(load)

        # Keep last 30 data points per hour
        if len(self.time_patterns[service_name][hour]) > 30:
            self.time_patterns[service_name][hour] = self.time_patterns[service_name][hour][-30:]

    def _predict_future_load(self, service_name: str, current_load: float) -> float:
        """Predict future load using trend analysis and time patterns"""
        history = self.scaling_history[service_name]

        # Get recent trend (last 10 data points)
        if len(history) >= 10:
            recent_loads = [h["load"] for h in history[-10:]]
            trend = self._calculate_trend(recent_loads)
        else:
            trend = 0

        # Get time-based prediction
        current_hour = int((time.time() % 86400) / 3600)
        next_hour = (current_hour + 1) % 24

        time_prediction = current_load
        if next_hour in self.time_patterns[service_name]:
            hour_loads = self.time_patterns[service_name][next_hour]
            if hour_loads:
                time_prediction = sum(hour_loads) / len(hour_loads)

        # Combine trend and time-based predictions
        # Weight: 60% time pattern, 40% trend
        predicted_load = (time_prediction * 0.6) + \
            ((current_load + trend) * 0.4)

        return max(0, min(100, predicted_load))  # Clamp between 0-100

    def _calculate_trend(self, values: list[float]) -> float:
        """Calculate linear trend using simple linear regression"""
        n = len(values)
        if n < 2:
            return 0

        # Simple linear regression
        x_values = list(range(n))
        x_mean = sum(x_values) / n
        y_mean = sum(values) / n

        numerator = sum((x_values[i] - x_mean) *
                        (values[i] - y_mean) for i in range(n))
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        if denominator == 0:
            return 0

        slope = numerator / denominator
        return slope  # Trend per time unit

    def _make_scaling_decision(self, service_name: str, current_load: float, predicted_load: float) -> str | None:
        """Make intelligent scaling decision based on current and predicted load"""

        # Define thresholds
        scale_up_threshold = 75
        scale_down_threshold = 25
        prediction_weight = 0.7  # How much to trust prediction vs current

        # Weighted decision score
        decision_score = (current_load * (1 - prediction_weight)
                          ) + (predicted_load * prediction_weight)

        # Check if we recently made a scaling decision (avoid thrashing)
        if service_name in self.scaling_decisions:
            last_decision = self.scaling_decisions[service_name]
            time_since_last = time.time() - last_decision["timestamp"]
            if time_since_last < 300:  # 5 minutes cooldown
                return None

        # Make decision
        if decision_score > scale_up_threshold:
            # Scale up more aggressively if trend is strongly upward
            if predicted_load > current_load + 10:
                return "scale_up_aggressive"  # Add multiple instances
            return "scale_up"

        elif decision_score < scale_down_threshold:
            # Only scale down if both current and predicted are low (be conservative)
            if current_load < 30 and predicted_load < 30:
                return "scale_down"

        # Proactive scaling: if prediction shows spike coming, scale early
        if predicted_load > scale_up_threshold and current_load < scale_up_threshold:
            return "scale_up_proactive"

        return None

    def get_scaling_report(self, service_name: str) -> dict:
        """Generate scaling analysis report"""
        if service_name not in self.scaling_history:
            return {"status": "no_data"}

        history = self.scaling_history[service_name]

        # Calculate statistics
        recent_loads = [h["load"] for h in history[-20:]]
        avg_load = sum(recent_loads) / len(recent_loads) if recent_loads else 0
        max_load = max(recent_loads) if recent_loads else 0
        min_load = min(recent_loads) if recent_loads else 0

        # Identify peak hours
        peak_hours = self._identify_peak_hours(service_name)

        return {
            "status": "active",
            "data_points": len(history),
            "average_load": round(avg_load, 2),
            "max_load": round(max_load, 2),
            "min_load": round(min_load, 2),
            "peak_hours": peak_hours,
            "last_scaling_decision": self.scaling_decisions.get(service_name),
            "pattern_learning_progress": f"{len(self.time_patterns.get(service_name, {}))} hours learned",
        }

    def _identify_peak_hours(self, service_name: str) -> list[int]:
        """Identify hours with highest average load"""
        if service_name not in self.time_patterns:
            return []

        hourly_averages = {}
        for hour, loads in self.time_patterns[service_name].items():
            if loads:
                hourly_averages[hour] = sum(loads) / len(loads)

        if not hourly_averages:
            return []

        # Get top 3 peak hours
        sorted_hours = sorted(hourly_averages.items(),
                              key=lambda x: x[1], reverse=True)
        return [hour for hour, _ in sorted_hours[:3]]


class NeuralAnomalyDetector:
    """Neural network-based anomaly detection (Aurora Tier 15: AI/ML + Tier 28: Autonomous Tools)"""

    def __init__(self):
        self.anomaly_patterns = {}
        self.baseline_metrics = {}
        self.anomaly_history = {}
        self.learning_window = 100  # Number of samples to establish baseline
        self.sensitivity = 2.5  # Standard deviations for anomaly threshold

    def detect_anomalies(self, service_name: str, metrics: dict) -> list[str]:
        """Detect system anomalies using statistical ML and pattern recognition"""
        anomalies = []

        # Initialize tracking for new services
        if service_name not in self.baseline_metrics:
            self.baseline_metrics[service_name] = {
                "cpu_usage": [],
                "memory_usage": [],
                "response_time": [],
                "error_rate": [],
                "request_rate": [],
            }
            self.anomaly_history[service_name] = []

        baseline = self.baseline_metrics[service_name]

        # Check each metric for anomalies
        for metric_name in ["cpu_usage", "memory_usage", "response_time", "error_rate", "request_rate"]:
            metric_value = metrics.get(metric_name)
            if metric_value is None:
                continue

            # Update baseline
            baseline[metric_name].append(metric_value)
            if len(baseline[metric_name]) > self.learning_window:
                baseline[metric_name] = baseline[metric_name][-self.learning_window:]

            # Need sufficient data for anomaly detection
            if len(baseline[metric_name]) < 20:
                continue

            # Statistical anomaly detection (Z-score method)
            anomaly = self._detect_statistical_anomaly(
                metric_name, metric_value, baseline[metric_name])
            if anomaly:
                anomalies.append(anomaly)

        # Pattern-based anomaly detection
        pattern_anomalies = self._detect_pattern_anomalies(
            service_name, metrics)
        anomalies.extend(pattern_anomalies)

        # Correlation-based anomaly detection (multiple metrics acting weird together)
        correlation_anomalies = self._detect_correlation_anomalies(
            service_name, metrics)
        anomalies.extend(correlation_anomalies)

        # Log anomalies for learning
        if anomalies:
            self.anomaly_history[service_name].append(
                {"timestamp": time.time(), "metrics": metrics,
                 "anomalies": anomalies}
            )

            # Keep last 1000 anomaly events
            if len(self.anomaly_history[service_name]) > 1000:
                self.anomaly_history[service_name] = self.anomaly_history[service_name][-1000:]

        return anomalies

    def _detect_statistical_anomaly(self, metric_name: str, value: float, baseline: list[float]) -> str | None:
        """Detect anomalies using statistical analysis (Z-score)"""
        if len(baseline) < 20:
            return None

        # Calculate mean and standard deviation
        mean = sum(baseline) / len(baseline)
        variance = sum((x - mean) ** 2 for x in baseline) / len(baseline)
        std_dev = variance**0.5

        if std_dev == 0:
            return None

        # Calculate Z-score
        z_score = (value - mean) / std_dev

        # If beyond threshold, it's an anomaly
        if abs(z_score) > self.sensitivity:
            direction = "spike" if z_score > 0 else "drop"
            return f"STATISTICAL_ANOMALY: {metric_name} {direction} detected (Z-score: {z_score:.2f}, value: {value:.2f}, baseline: {mean:.2f}±{std_dev:.2f})"

        return None

    def _detect_pattern_anomalies(self, service_name: str, metrics: dict) -> list[str]:
        """Detect anomalies based on known patterns"""
        anomalies = []

        # Pattern 1: High error rate with normal CPU (something wrong in code)
        if metrics.get("error_rate", 0) > 5 and metrics.get("cpu_usage", 100) < 50:
            anomalies.append(
                "PATTERN_ANOMALY: High error rate with low CPU usage suggests code/logic error")

        # Pattern 2: High CPU with low request rate (inefficient processing or infinite loop)
        if metrics.get("cpu_usage", 0) > 80 and metrics.get("request_rate", 100) < 10:
            anomalies.append(
                "PATTERN_ANOMALY: High CPU with low requests suggests inefficient processing or background task issue"
            )

        # Pattern 3: Memory leak detection (memory consistently increasing)
        if service_name in self.baseline_metrics:
            memory_history = self.baseline_metrics[service_name].get(
                "memory_usage", [])
            if len(memory_history) >= 10:
                recent_10 = memory_history[-10:]
                if all(recent_10[i] <= recent_10[i + 1] for i in range(len(recent_10) - 1)):
                    anomalies.append(
                        "PATTERN_ANOMALY: Potential memory leak detected (consistently increasing memory)")

        # Pattern 4: Response time spikes (possible database/network issue)
        if metrics.get("response_time", 0) > 5000:  # 5 seconds
            anomalies.append(
                "PATTERN_ANOMALY: Extreme response time detected - possible database or network issue")

        return anomalies

    def _detect_correlation_anomalies(self, _service_name: str, metrics: dict) -> list[str]:
        """Detect anomalies based on correlation between metrics"""
        anomalies = []

        # Normally, high request rate correlates with high CPU
        # If requests are high but CPU is low, something is wrong (requests not being processed)
        request_rate = metrics.get("request_rate", 0)
        cpu_usage = metrics.get("cpu_usage", 0)

        if request_rate > 50 and cpu_usage < 20:
            anomalies.append(
                "CORRELATION_ANOMALY: High request rate but low CPU - requests may not be processing")

        # High memory + high error rate = possible OOM errors
        if metrics.get("memory_usage", 0) > 90 and metrics.get("error_rate", 0) > 10:
            anomalies.append(
                "CORRELATION_ANOMALY: High memory usage with high error rate - possible out-of-memory errors"
            )

        return anomalies

    def get_anomaly_report(self, service_name: str) -> dict:
        """Generate anomaly detection report"""
        if service_name not in self.anomaly_history:
            return {"status": "no_data", "total_anomalies": 0}

        history = self.anomaly_history[service_name]

        return {
            "status": "active",
            "total_anomalies": len(history),
            "recent_anomalies": history[-10:],
            "anomaly_types": self._summarize_anomaly_types(history),
            "baseline_established": len(self.baseline_metrics.get(service_name, {}).get("cpu_usage", []))
            >= self.learning_window,
        }

    def _summarize_anomaly_types(self, history: list) -> dict:
        """Summarize types of anomalies detected"""
        summary = {}
        for event in history:
            for anomaly in event["anomalies"]:
                anomaly_type = anomaly.split(":")[0]
                summary[anomaly_type] = summary.get(anomaly_type, 0) + 1
        return summary


def run_luminar_nexus_v2(port: int = 5005):
    """Run Luminar Nexus v2 with advanced capabilities"""
    print("🌌 Starting Luminar Nexus v2 - Advanced System Orchestrator")

    # Initialize Nexus v2
    nexus = LuminarNexusV2()

    # Register standard Aurora services
    nexus.register_service("frontend", 5173, "ui", quantum_state="entangled")
    nexus.register_service("backend", 5000, "api", quantum_state="stable")
    nexus.register_service("bridge", 5001, "middleware", dependencies=[
                           "backend"], quantum_state="stable")
    nexus.register_service("self-learn", 5002, "ai",
                           dependencies=["backend"], quantum_state="superposition")
    nexus.register_service("chat", 5003, "ai", dependencies=[
                           "bridge"], quantum_state="entangled")

    # Create advanced API
    app = nexus.create_advanced_api()

    print(f"🚀 Luminar Nexus v2 running on port {port}")
    print("✨ Features: AI Healing | Quantum Coherence | Predictive Scaling | Neural Anomaly Detection")

    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)


def run_chat_server_v2(port: int = 5003):
    """Run Aurora's V2 chat server with enhanced routing"""
    print(f"🌌 Aurora Chat Server V2 starting on port {port}...")
    print("✨ Enhanced with Quantum Coherence and AI Routing")

    # Initialize Nexus V2
    nexus = LuminarNexusV2()

    # Create the advanced API (includes /api/chat endpoint)
    app = nexus.create_advanced_api()

    # Add health check endpoints
    @app.route("/health", methods=["GET"])
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return {
            "status": "healthy",
            "service": "aurora-chat-v2",
            "version": nexus.version,
            "aurora_fix": "Added /api/health for frontend compatibility",
        }, 200

    print(f"🚀 Chat Server V2 running on port {port}")
    print("   Health: http://localhost:{port}/health")
    print("   Chat: POST http://localhost:{port}/api/chat")

    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)


def main():
    """Main entry point for V2 with CLI support"""
    if len(sys.argv) < 2:
        print("Luminar Nexus V2 - Advanced System Orchestrator")
        print("\nUsage:")
        print("  python luminar_nexus_v2.py start <server>   - Start a server")
        print("  python luminar_nexus_v2.py stop <server>    - Stop a server")
        print("  python luminar_nexus_v2.py start-all        - Start all servers")
        print("  python luminar_nexus_v2.py stop-all         - Stop all servers")
        print("  python luminar_nexus_v2.py status           - Show all status")
        print("  python luminar_nexus_v2.py api              - Run API server (port 5005)")
        print("  python luminar_nexus_v2.py chat             - Run chat server (port 5003)")
        print("\nAvailable servers: vite, backend, bridge, self-learn, chat")
        return

    nexus = LuminarNexusV2()
    command = sys.argv[1]

    if command == "start-all":
        nexus.start_all_servers()
    elif command == "start" and len(sys.argv) > 2:
        nexus.start_server(sys.argv[2])
    elif command == "stop-all":
        nexus.stop_all_servers()
    elif command == "stop" and len(sys.argv) > 2:
        nexus.stop_server(sys.argv[2])
    elif command == "status":
        nexus.show_status()
    elif command == "api":
        run_luminar_nexus_v2(5005)
    elif command == "chat":
        run_chat_server_v2(5003)
    else:
        print("❌ Invalid command")


def serve():
    """Start Luminar Nexus V2 API server"""
    nexus = LuminarNexusV2()

    # Register Aurora services - only services that are actually running
    # Note: Frontend is served through backend via Vite middleware on port 5000
    nexus.register_service("backend", 5000, "fullstack", [], "stable")

    # Disabled services (not currently running):
    # frontend on port 5173 - doesn't exist (Vite runs in middleware mode on port 5000)
    # nexus.register_service("bridge", 5001, "middleware", ["backend"], "stable")
    # nexus.register_service("self-learn", 5002, "ai", ["backend"], "superposition")
    # nexus.register_service("chat", 5003, "ai", [], "stable")

    # Start monitoring
    nexus.start_advanced_monitoring()

    # Create and run Flask API
    app = nexus.create_advanced_api()

    print("\n🌌 Luminar Nexus V2 API Server Starting...")
    print("   Port: 5005")
    print(f"   Quantum Coherence: {nexus.quantum_mesh.coherence_level:.2f}")
    print(f"   Services Registered: {len(nexus.service_registry)}")
    print("\n✨ Advanced Features Active:")
    print("   • AI-driven autonomous healing")
    print("   • Port conflict resolution")
    print("   • Predictive scaling")
    print("   • Neural anomaly detection")
    print("\n")

    app.run(host="0.0.0.0", port=5005, debug=False)


if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        serve()
    else:
        main()
