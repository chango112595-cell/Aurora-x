import time

from logging_system import AuroraLogger


class RepairEngine:
    def __init__(self, process_manager, registry):
        self.process_manager = process_manager
        self.registry = registry
        self.logger = AuroraLogger("RepairEngine")

    def check_process(self, name, pid):
        try:
            os.kill(pid, 0)
            return True
        except:
            return False

    def start_autoheal_loop(self):
        self.logger.warn("Auto-heal loop started.")

        while True:
            active = self.registry.get("active_processes") or {}

            for name, pid in active.items():
                alive = self.check_process(name, pid)
                if not alive:
                    self.logger.error(f"Module {name} crashed. Restarting...")
                    cmd = self.registry.get("modules")[name]["command"]
                    self.process_manager.start_process(name, cmd)

            time.sleep(2)
