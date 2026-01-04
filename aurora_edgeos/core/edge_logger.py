import time


class EdgeLogger:
    def __init__(self, device_id):
        self.device_id = device_id

    def _log(self, level, msg):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] [{self.device_id}] [{level}] {msg}")

    def info(self, msg):
        self._log("INFO", msg)

    def warn(self, msg):
        self._log("WARN", msg)

    def error(self, msg):
        self._log("ERROR", msg)
