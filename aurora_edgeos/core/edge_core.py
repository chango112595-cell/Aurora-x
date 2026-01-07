import threading
import time
import uuid

from ..comm.edge_comm import EdgeComm
from .edge_logger import EdgeLogger
from .edge_registry import EdgeRegistry
from .edge_sandbox import EdgeSandbox


class AuroraEdgeCore:
    def __init__(self, device_type="generic", device_id=None, config=None):
        self.device_type = device_type
        self.device_id = device_id or str(uuid.uuid4())
        self.config = config or {}

        self.registry = EdgeRegistry(self.device_id)
        self.logger = EdgeLogger(self.device_id)
        self.sandbox = EdgeSandbox(self.device_id)
        self.comm = EdgeComm(self.device_id)

        self.running = False

    def start(self):
        self.logger.info(f"🌍 Aurora EdgeOS starting on device {self.device_id}")
        self.running = True

        threading.Thread(target=self._heartbeat_loop, daemon=True).start()

    def stop(self):
        self.running = False
        self.logger.info("🛑 Aurora EdgeOS stopped.")

    def _heartbeat_loop(self):
        while self.running:
            self.comm.send_heartbeat(self.device_type)
            time.sleep(2)

    def execute_task(self, task):
        """Executes a task securely inside the sandbox"""
        return self.sandbox.run(task)
