class EdgeSandbox:
    def __init__(self, device_id):
        self.device_id = device_id

    def run(self, task):
        """Device-protected task executor"""
        safe_globals = {}
        safe_locals = {"output": None}

        try:
            exec(task, safe_globals, safe_locals)
            return safe_locals["output"]
        except Exception as e:
            return {"error": str(e)}
