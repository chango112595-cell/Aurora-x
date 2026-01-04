import datetime

class AuroraLogger:
    def __init__(self, source):
        self.source = source

    def log(self, level, msg):
        print(f"[{datetime.datetime.now()}] [{self.source}] [{level}] {msg}")

    def info(self, msg): self.log("INFO", msg)
    def warn(self, msg): self.log("WARN", msg)
    def error(self, msg): self.log("ERROR", msg)
