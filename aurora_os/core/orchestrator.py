#!/usr/bin/env python3
import time
import argparse
from process_manager import ProcessManager
from repair_engine import RepairEngine
from registry import Registry
from module_loader import ModuleLoader
from update_engine import UpdateEngine
from event_bus import EventBus
from logging_system import AuroraLogger
from security_sandbox import SecuritySandbox

class AuroraOrchestrator:
    def __init__(self):
        self.logger = AuroraLogger("AuroraOrchestrator")
        self.registry = Registry()
        self.process_manager = ProcessManager(self.registry)
        self.repair_engine = RepairEngine(self.process_manager, self.registry)
        self.module_loader = ModuleLoader(self.registry, self.process_manager)
        self.update_engine = UpdateEngine(self.registry)
        self.event_bus = EventBus()
        self.security = SecuritySandbox()

        self.logger.info("AuroraOS Orchestrator initialized.")

    def start(self):
        self.logger.info("Starting all Aurora services...")
        self.module_loader.load_all_modules()
        self.process_manager.start_all()
        self.logger.info("All Aurora modules started.")

    def stop(self):
        self.logger.info("Stopping all Aurora services...")
        self.process_manager.stop_all()
        self.logger.info("All Aurora modules stopped.")

    def restart(self):
        self.logger.warn("Restarting Aurora services...")
        self.stop()
        time.sleep(1)
        self.start()
        self.logger.info("Restart complete.")

    def status(self):
        self.logger.info("Displaying Aurora system status...")
        statuses = self.process_manager.get_status()
        for name, stat in statuses.items():
            print(f"{name}: {stat}")

    def update(self):
        self.logger.warn("Checking for updates...")
        self.update_engine.check_and_apply_updates()

    def autoheal(self):
        self.logger.info("Entering auto-heal loop.")
        self.repair_engine.start_autoheal_loop()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["start", "stop", "restart", "status", "update", "heal"])
    args = parser.parse_args()

    orchestrator = AuroraOrchestrator()

    match args.command:
        case "start": orchestrator.start()
        case "stop": orchestrator.stop()
        case "restart": orchestrator.restart()
        case "status": orchestrator.status()
        case "update": orchestrator.update()
        case "heal": orchestrator.autoheal()

if __name__ == "__main__":
    main()
