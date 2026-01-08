import subprocess

from logging_system import AuroraLogger


class ProcessManager:
    def __init__(self, registry):
        self.registry = registry
        self.logger = AuroraLogger("ProcessManager")
        self.processes = {}

    def start_process(self, name, command):
        self.logger.info(f"Starting module: {name}")

        if isinstance(command, list):
            cmd = command
        else:
            cmd = command.split(" ")

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        self.processes[name] = proc
        self.registry.set("active_processes", name, proc.pid)

        self.logger.info(f"Module {name} running with PID {proc.pid}")

    def stop_process(self, name):
        if name not in self.processes:
            self.logger.warn(f"Module {name} not running.")
            return

        proc = self.processes[name]
        self.logger.info(f"Stopping module: {name}")

        proc.terminate()
        try:
            proc.wait(timeout=3)
        except:
            proc.kill()

        del self.processes[name]
        self.registry.delete("active_processes", name)

    def start_all(self):
        modules = self.registry.get("modules") or {}

        for module_name, module_data in modules.items():
            self.start_process(module_name, module_data["command"])

    def stop_all(self):
        for name in list(self.processes.keys()):
            self.stop_process(name)

    def get_status(self):
        status = {}
        for name, proc in self.processes.items():
            alive = proc.poll() is None
            status[name] = "RUNNING" if alive else "STOPPED"
        return status
