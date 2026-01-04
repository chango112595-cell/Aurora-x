import logging
import time

logger = logging.getLogger(__name__)


class LifecycleHook:
    def __init__(self, name, callback):
        self.name = name
        self.callback = callback

    def execute(self, context):
        try:
            result = self.callback(context)
            return {"ok": True, "hook": self.name, "result": result}
        except Exception as e:
            return {"ok": False, "hook": self.name, "error": str(e)}


class ModuleLifecycle:
    def __init__(self):
        self.pre_init_hooks = []
        self.post_init_hooks = []
        self.pre_exec_hooks = []
        self.post_exec_hooks = []
        self.pre_cleanup_hooks = []
        self.post_cleanup_hooks = []

    def add_hook(self, phase, hook):
        hook_list = getattr(self, f"{phase}_hooks", None)
        if hook_list is not None:
            hook_list.append(hook)

    def _run_hooks(self, hooks, context):
        results = []
        for hook in hooks:
            results.append(hook.execute(context))
        return results

    def run_init(self, module_path, ctx=None):
        context = {"module_path": module_path, "ctx": ctx or {}, "phase": "init"}
        pre_results = self._run_hooks(self.pre_init_hooks, context)
        start = time.time()
        try:
            spec = self._load_module(module_path, "init")
            if spec and hasattr(spec, "initialize"):
                result = spec.initialize()
            else:
                result = {"status": "ok", "default": True}
        except Exception as e:
            result = {"status": "error", "error": str(e)}
        duration = time.time() - start
        context["result"] = result
        context["duration"] = duration
        post_results = self._run_hooks(self.post_init_hooks, context)
        return {
            "phase": "init",
            "result": result,
            "duration_ms": duration * 1000,
            "pre_hooks": pre_results,
            "post_hooks": post_results,
        }

    def run_execute(self, module_path, payload=None):
        context = {"module_path": module_path, "payload": payload, "phase": "execute"}
        pre_results = self._run_hooks(self.pre_exec_hooks, context)
        start = time.time()
        try:
            spec = self._load_module(module_path, "execute")
            if spec and hasattr(spec, "execute"):
                result = spec.execute(payload or {})
            else:
                result = {"status": "error", "error": "No execute function"}
        except Exception as e:
            result = {"status": "error", "error": str(e)}
        duration = time.time() - start
        context["result"] = result
        context["duration"] = duration
        post_results = self._run_hooks(self.post_exec_hooks, context)
        return {
            "phase": "execute",
            "result": result,
            "duration_ms": duration * 1000,
            "pre_hooks": pre_results,
            "post_hooks": post_results,
        }

    def run_cleanup(self, module_path):
        context = {"module_path": module_path, "phase": "cleanup"}
        pre_results = self._run_hooks(self.pre_cleanup_hooks, context)
        start = time.time()
        try:
            spec = self._load_module(module_path, "cleanup")
            if spec and hasattr(spec, "cleanup"):
                result = spec.cleanup()
            else:
                result = {"status": "ok", "default": True}
        except Exception as e:
            result = {"status": "error", "error": str(e)}
        duration = time.time() - start
        context["result"] = result
        post_results = self._run_hooks(self.post_cleanup_hooks, context)
        return {
            "phase": "cleanup",
            "result": result,
            "duration_ms": duration * 1000,
            "pre_hooks": pre_results,
            "post_hooks": post_results,
        }

    def _load_module(self, path, phase):
        import importlib.util

        try:
            spec = importlib.util.spec_from_file_location(f"module_{phase}", path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
        except Exception as e:
            logger.error(f"Failed to load module: {e}")
        return None
