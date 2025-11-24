#!/usr/bin/env python3
"""
Aurora Advanced Process Supervisor
Self-healing service orchestration with health monitoring and auto-restart
Built by Aurora in seconds - because experts don't need weeks.
"""

import json
import logging
import os
import signal
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from threading import Event, Thread

import psutil
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("/tmp/aurora_supervisor.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@dataclass
class ServiceConfig:
    """Configuration for a monitored service"""

    name: str
    port: int
    start_command: str
    working_dir: str
    health_endpoint: str | None = None
    dependencies: list[str] = None
    max_restarts: int = 5
    restart_delay: int = 5
    env_activation: str | None = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class ServiceState:
    """Runtime state of a service"""

    name: str
    status: str  # stopped, starting, running, failed, crashed, paused
    pid: int | None = None
    port: int = 0
    restart_count: int = 0
    last_restart: str | None = None
    last_health_check: str | None = None
    health_status: str = "unknown"
    uptime_seconds: float = 0
    crash_count: int = 0
    paused: bool = False  # If True, don't auto-restart


class AuroraSupervisor:
    """Advanced service supervisor with self-healing capabilities"""

    def __init__(self, config_file: str = "aurora_supervisor_config.json"):
        self.config_file = Path(config_file)
        self.services: dict[str, ServiceConfig] = {}
        self.states: dict[str, ServiceState] = {}
        self.processes: dict[str, subprocess.Popen] = {}
        self.shutdown_event = Event()
        self.monitor_threads: dict[str, Thread] = {}

        self.load_config()

    def load_config(self):
        """Load or create service configuration"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                config_data = json.load(f)
                for svc_data in config_data["services"]:
                    svc = ServiceConfig(**svc_data)
                    self.services[svc.name] = svc
                    self.states[svc.name] = ServiceState(name=svc.name, status="stopped", port=svc.port)
        else:
            # Create default config
            self.create_default_config()

    def create_default_config(self):
        """Create default Aurora-X service configuration"""
        services = [
            ServiceConfig(
                name="aurora-ui",
                port=5000,
                start_command="npm run dev",
                working_dir="/workspaces/Aurora-x",
                health_endpoint="http://localhost:5000/api/health",
                dependencies=[],
            ),
            ServiceConfig(
                name="aurora-backend",
                port=5001,
                start_command="uvicorn aurora_x.serve:app --host 0.0.0.0 --port 5001",
                working_dir="/workspaces/Aurora-x",
                health_endpoint="http://localhost:5001/health",
                dependencies=[],
                env_activation=". .venv/bin/activate",
            ),
            ServiceConfig(
                name="self-learning",
                port=5002,
                start_command="python -m aurora_x.self_learn_server",
                working_dir="/workspaces/Aurora-x",
                health_endpoint="http://localhost:5002/health",
                dependencies=["aurora-backend"],
                env_activation=". .venv/bin/activate",
            ),
            ServiceConfig(
                name="file-server",
                port=8080,
                start_command="python3 -m http.server 8080 --directory /workspaces/Aurora-x",
                working_dir="/workspaces/Aurora-x",
                health_endpoint=None,
                dependencies=[],
            ),
        ]

        for svc in services:
            self.services[svc.name] = svc
            self.states[svc.name] = ServiceState(name=svc.name, status="stopped", port=svc.port)

        self.save_config()

    def save_config(self):
        """Save current configuration"""
        config_data = {"services": [asdict(svc) for svc in self.services.values()]}
        with open(self.config_file, "w") as f:
            json.dump(config_data, f, indent=2)

    def check_port(self, port: int) -> bool:
        """Check if a port is listening"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == "LISTEN":
                return True
        return False

    def check_health(self, service: ServiceConfig) -> bool:
        """Check service health via HTTP endpoint"""
        if not service.health_endpoint:
            # No health endpoint, just check port
            return self.check_port(service.port)

        try:
            response = requests.get(service.health_endpoint, timeout=2)
            return response.status_code == 200
        except Exception:
            # If health endpoint fails, fall back to port check
            # Don't kill a running service just because health endpoint is wrong
            port_alive = self.check_port(service.port)
            if port_alive:
                logger.debug(f"Health endpoint failed for {service.name}, but port {service.port} is listening")
            return port_alive

    def get_process_for_port(self, port: int) -> int | None:
        """Get PID of process listening on port"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == "LISTEN":
                return conn.pid
        return None

    def start_service(self, service_name: str) -> bool:
        """Start a service"""
        service = self.services[service_name]
        state = self.states[service_name]

        # Clear paused flag when manually starting
        state.paused = False

        # Check dependencies first
        for dep in service.dependencies:
            dep_state = self.states.get(dep)
            if not dep_state or dep_state.status != "running":
                logger.warning(f"Dependency {dep} not running, waiting...")
                return False

        logger.info(f"Starting service: {service_name}")
        state.status = "starting"

        try:
            # Build command with environment activation if needed
            cmd = service.start_command
            if service.env_activation:
                cmd = f"{service.env_activation} && {cmd}"

            # Start process
            process = subprocess.Popen(
                cmd,
                shell=True,
                cwd=service.working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid,  # Create new process group
            )

            self.processes[service_name] = process

            # Wait a bit for startup
            time.sleep(3)

            # Check if it's actually running
            if self.check_port(service.port):
                state.status = "running"
                state.pid = self.get_process_for_port(service.port)
                state.uptime_seconds = 0
                logger.info(f"[OK] Service {service_name} started successfully on port {service.port}")
                return True
            else:
                state.status = "failed"
                logger.error(f"[ERROR] Service {service_name} failed to start")
                return False

        except Exception as e:
            state.status = "failed"
            logger.error(f"[ERROR] Error starting {service_name}: {e}")
            return False

    def stop_service(self, service_name: str, graceful: bool = True, pause: bool = True):
        """Stop a service

        Args:
            service_name: Name of the service to stop
            graceful: Try graceful shutdown before force kill
            pause: If True, mark as paused so auto-restart won't happen
        """
        state = self.states[service_name]
        logger.info(f"Stopping service: {service_name} (pause={pause})")

        # Mark as paused if requested - this prevents auto-restart
        if pause:
            state.paused = True
            state.status = "paused"

        # Stop monitoring thread
        if service_name in self.monitor_threads:
            self.shutdown_event.set()

        # Kill process
        if service_name in self.processes:
            process = self.processes[service_name]
            if graceful:
                process.terminate()
                time.sleep(2)
            if process.poll() is None:
                process.kill()
            del self.processes[service_name]

        # Also kill by port
        pid = self.get_process_for_port(state.port)
        if pid:
            try:
                os.killpg(os.getpgid(pid), signal.SIGTERM)
            except:
                pass

        if not pause:
            state.status = "stopped"
        state.pid = None
        logger.info(f"Service {service_name} stopped")

    def restart_service(self, service_name: str):
        """Restart a service with exponential backoff"""
        state = self.states[service_name]
        service = self.services[service_name]

        # Check restart limits
        if state.restart_count >= service.max_restarts:
            logger.error(f"⛔ Service {service_name} exceeded max restarts ({service.max_restarts})")
            state.status = "failed"
            return

        # Clear paused flag - restart means user wants it running
        state.paused = False

        # Exponential backoff
        delay = service.restart_delay * (2**state.restart_count)
        logger.info(f"[SYNC] Restarting {service_name} in {delay}s (attempt {state.restart_count + 1})")
        time.sleep(delay)

        # Stop and start - don't pause on restart
        self.stop_service(service_name, graceful=False, pause=False)
        time.sleep(2)

        if self.start_service(service_name):
            state.restart_count += 1
            state.last_restart = datetime.now().isoformat()
        else:
            state.crash_count += 1

    def monitor_service(self, service_name: str):
        """Monitor thread for a service"""
        service = self.services[service_name]
        state = self.states[service_name]

        logger.info(f"[EYE] Monitoring started for {service_name}")

        while not self.shutdown_event.is_set():
            time.sleep(10)  # Check every 10 seconds

            # Skip monitoring if service is paused
            if state.paused:
                logger.debug(f"Service {service_name} is paused, skipping monitoring")
                continue

            if state.status != "running":
                continue

            # Health check
            healthy = self.check_health(service)
            state.last_health_check = datetime.now().isoformat()

            if healthy:
                state.health_status = "healthy"
                state.uptime_seconds += 10
            else:
                state.health_status = "unhealthy"
                logger.warning(f"[WARN] Service {service_name} failed health check")

                # Only attempt restart if NOT paused
                if not state.paused:
                    state.status = "crashed"
                    self.restart_service(service_name)

    def start_all(self):
        """Start all services in dependency order"""
        logger.info("[LAUNCH] Starting all services...")

        # Build dependency graph and start in order
        started = set()
        max_iterations = len(self.services) * 2
        iteration = 0

        while len(started) < len(self.services) and iteration < max_iterations:
            iteration += 1

            for service_name, service in self.services.items():
                if service_name in started:
                    continue

                # Check if dependencies are met
                deps_met = all(dep in started for dep in service.dependencies)

                if deps_met:
                    if self.start_service(service_name):
                        started.add(service_name)

                        # Start monitoring thread
                        thread = Thread(target=self.monitor_service, args=(service_name,), daemon=True)
                        thread.start()
                        self.monitor_threads[service_name] = thread

            time.sleep(2)

        logger.info(f"[OK] Started {len(started)}/{len(self.services)} services")

    def stop_all(self):
        """Stop all services"""
        logger.info("[EMOJI] Stopping all services...")
        self.shutdown_event.set()

        for service_name in list(self.services.keys()):
            self.stop_service(service_name, pause=False)

        logger.info("All services stopped")

    def pause_service(self, service_name: str):
        """Pause a service (stop it and prevent auto-restart)"""
        logger.info(f"⏸️ Pausing service: {service_name}")
        self.stop_service(service_name, pause=True)

    def resume_service(self, service_name: str):
        """Resume a paused service"""
        state = self.states[service_name]
        logger.info(f"▶️ Resuming service: {service_name}")
        state.paused = False
        self.start_service(service_name)

    def get_status(self) -> dict:
        """Get current status of all services"""
        return {
            "timestamp": datetime.now().isoformat(),
            "services": {name: asdict(state) for name, state in self.states.items()},
        }

    def run_forever(self):
        """Run supervisor indefinitely"""
        logger.info("[TARGET] Aurora Supervisor running...")

        try:
            while not self.shutdown_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
            self.stop_all()


def main():
    """Entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Aurora Advanced Process Supervisor")
    parser.add_argument(
        "command", choices=["start", "stop", "pause", "resume", "restart", "status"], help="Command to execute"
    )
    parser.add_argument("--service", help="Specific service name (optional)")
    parser.add_argument("--config", default="aurora_supervisor_config.json", help="Config file path")

    args = parser.parse_args()

    supervisor = AuroraSupervisor(config_file=args.config)

    if args.command == "start":
        if args.service:
            supervisor.start_service(args.service)
        else:
            supervisor.start_all()
            supervisor.run_forever()

    elif args.command == "stop":
        if args.service:
            supervisor.stop_service(args.service, pause=True)  # Dashboard stop = pause
        else:
            supervisor.stop_all()

    elif args.command == "pause":
        if args.service:
            supervisor.pause_service(args.service)
        else:
            print("Error: --service required for pause command")

    elif args.command == "resume":
        if args.service:
            supervisor.resume_service(args.service)
        else:
            print("Error: --service required for resume command")

    elif args.command == "restart":
        if args.service:
            supervisor.restart_service(args.service)
        else:
            supervisor.stop_all()
            time.sleep(2)
            supervisor.start_all()
            supervisor.run_forever()

    elif args.command == "status":
        status = supervisor.get_status()
        print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
