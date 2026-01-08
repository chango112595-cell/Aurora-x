import runpy
import traceback
from types import SimpleNamespace


class PluginSandbox:
    """
    Extremely lightweight "soft" sandbox — restricts globals, prevents access
    to critical Aurora internals, and isolates execution namespace.
    """

    SAFE_GLOBALS = {
        "__builtins__": {
            "print": print,
            "range": range,
            "len": len,
            "min": min,
            "max": max,
            "sum": sum,
            "abs": abs,
        }
    }

    def __init__(self, plugin_path: str):
        self.plugin_path = plugin_path
        self.last_error = None
        self.context = {}

    def execute(self):
        try:
            namespace = {}
            runpy.run_path(self.plugin_path, init_globals=self.SAFE_GLOBALS, run_name="__main__")
            self.context = namespace
            return True

        except Exception:
            self.last_error = traceback.format_exc()
            return False

    def get_last_error(self):
        return self.last_error


def run_in_sandbox(path: str):
    s = PluginSandbox(path)
    ok = s.execute()
    return SimpleNamespace(ok=ok, error=s.get_last_error())
