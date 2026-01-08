import json
from datetime import datetime
from pathlib import Path

CATEGORIES = [
    "connector",
    "processor",
    "analyzer",
    "generator",
    "transformer",
    "validator",
    "formatter",
    "optimizer",
    "monitor",
    "integrator",
]

CATEGORY_TEMPLATES = {
    "connector": """class {class_name}:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}
        self.connection = None

    def execute(self, payload):
        start = time.time()
        try:
            endpoint = payload.get("endpoint", "default")
            data = payload.get("data", {{}})
            result = {{"connected": True, "endpoint": endpoint, "response": {{"status": "ok", "data_size": len(str(data))}}}}
            return {{"status": "ok", "duration_ms": (time.time()-start)*1000, "result": result}}
        except Exception as e:
            return {{"status": "error", "error": str(e), "duration_ms": (time.time()-start)*1000}}""",
    "processor": """class {class_name}:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}

    def execute(self, payload):
        start = time.time()
        try:
            items = payload.get("items", [])
            processed = [self._process_item(item) for item in items]
            return {{"status": "ok", "processed_count": len(processed), "results": processed, "duration_ms": (time.time()-start)*1000}}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}

    def _process_item(self, item):
        if isinstance(item, dict):
            return {{k: v for k, v in item.items() if v is not None}}
        return item""",
    "analyzer": """class {class_name}:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}

    def execute(self, payload):
        start = time.time()
        try:
            data = payload.get("data", {{}})
            analysis = {{"field_count": len(data) if isinstance(data, dict) else 0, "type": type(data).__name__, "size": len(str(data))}}
            return {{"status": "ok", "analysis": analysis, "duration_ms": (time.time()-start)*1000}}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}""",
    "generator": """class {class_name}:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}

    def execute(self, payload):
        start = time.time()
        try:
            template = payload.get("template", "default")
            count = payload.get("count", 1)
            generated = [{{"id": i, "template": template, "data": {{}}}} for i in range(count)]
            return {{"status": "ok", "generated": generated, "count": len(generated), "duration_ms": (time.time()-start)*1000}}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}""",
    "transformer": """class {class_name}:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}

    def execute(self, payload):
        start = time.time()
        try:
            source = payload.get("source", {{}})
            mapping = payload.get("mapping", {{}})
            transformed = {{mapping.get(k, k): v for k, v in source.items()}} if isinstance(source, dict) else source
            return {{"status": "ok", "transformed": transformed, "duration_ms": (time.time()-start)*1000}}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}""",
    "validator": """class {class_name}:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}

    def execute(self, payload):
        start = time.time()
        try:
            data = payload.get("data", {{}})
            rules = payload.get("rules", [])
            errors = []
            for rule in rules:
                field = rule.get("field")
                required = rule.get("required", False)
                if required and field not in data:
                    errors.append(f"Missing required field: {{field}}")
            valid = len(errors) == 0
            return {{"status": "ok", "valid": valid, "errors": errors, "duration_ms": (time.time()-start)*1000}}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}""",
    "formatter": """class {class_name}:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}

    def execute(self, payload):
        start = time.time()
        try:
            data = payload.get("data", {{}})
            fmt = payload.get("format", "json")
            if fmt == "json":
                import json
                formatted = json.dumps(data, indent=2)
            else:
                formatted = str(data)
            return {{"status": "ok", "formatted": formatted, "format": fmt, "duration_ms": (time.time()-start)*1000}}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}""",
    "optimizer": """class {class_name}:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}

    def execute(self, payload):
        start = time.time()
        try:
            data = payload.get("data", [])
            strategy = payload.get("strategy", "default")
            if isinstance(data, list):
                optimized = sorted(set(data))
            else:
                optimized = data
            return {{"status": "ok", "optimized": optimized, "strategy": strategy, "duration_ms": (time.time()-start)*1000}}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}""",
    "monitor": """class {class_name}:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}
        self.metrics = {{}}

    def execute(self, payload):
        start = time.time()
        try:
            target = payload.get("target", "system")
            self.metrics[target] = {{"checked_at": time.time(), "status": "healthy"}}
            return {{"status": "ok", "metrics": self.metrics, "duration_ms": (time.time()-start)*1000}}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}""",
    "integrator": """class {class_name}:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}

    def execute(self, payload):
        start = time.time()
        try:
            sources = payload.get("sources", [])
            merged = {{}}
            for src in sources:
                if isinstance(src, dict):
                    merged.update(src)
            return {{"status": "ok", "integrated": merged, "source_count": len(sources), "duration_ms": (time.time()-start)*1000}}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}""",
}


class ModuleGenerator:
    def __init__(self, output_dir="generated_modules"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.registry = {}

    def generate_manifest(self, count=550):
        manifest = []
        for i in range(count):
            category = CATEGORIES[i % len(CATEGORIES)]
            module_id = f"{i + 1:04d}"
            manifest.append(
                {
                    "id": module_id,
                    "name": f"{category.capitalize()}_{module_id}",
                    "category": category,
                    "version": "1.0.0",
                }
            )
        return manifest

    def _generate_init(self, module_id, name, category):
        return f'''"""
Aurora Module: {name}
ID: {module_id}
Category: {category}
Generated: {datetime.utcnow().isoformat()}Z
"""
import time

class {name}Init:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}
        self.initialized = False

    def initialize(self):
        self.initialized = True
        return {{"status": "ok", "module": "{name}"}}
'''

    def _generate_execute(self, module_id, name, category):
        template = CATEGORY_TEMPLATES.get(category, CATEGORY_TEMPLATES["processor"])
        class_name = f"{name}Execute"
        code = f'''"""
Aurora Module: {name}
ID: {module_id}
Category: {category}
Generated: {datetime.utcnow().isoformat()}Z
"""
import time

{template.format(class_name=class_name)}

def execute(payload=None):
    instance = {class_name}()
    return instance.execute(payload or {{}})
'''
        return code

    def _generate_cleanup(self, module_id, name, category):
        return f'''"""
Aurora Module: {name}
ID: {module_id}
Category: {category}
Generated: {datetime.utcnow().isoformat()}Z
"""
import time

class {name}Cleanup:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}

    def cleanup(self):
        return {{"status": "ok", "cleaned": True}}

def cleanup():
    instance = {name}Cleanup()
    return instance.cleanup()
'''

    def generate_module(self, spec):
        module_id = spec["id"]
        name = spec["name"]
        category = spec["category"]
        module_dir = self.output_dir / category
        module_dir.mkdir(parents=True, exist_ok=True)
        files = []
        init_path = module_dir / f"{category}_{module_id}_init.py"
        init_path.write_text(self._generate_init(module_id, name, category))
        files.append(str(init_path))
        exec_path = module_dir / f"{category}_{module_id}_execute.py"
        exec_path.write_text(self._generate_execute(module_id, name, category))
        files.append(str(exec_path))
        cleanup_path = module_dir / f"{category}_{module_id}_cleanup.py"
        cleanup_path.write_text(self._generate_cleanup(module_id, name, category))
        files.append(str(cleanup_path))
        self.registry[module_id] = {
            "id": module_id,
            "name": name,
            "category": category,
            "files": files,
        }
        return {"id": module_id, "files": files}

    def generate_all(self, manifest):
        results = []
        for spec in manifest:
            result = self.generate_module(spec)
            results.append(result)
        registry_path = self.output_dir / "modules_registry.json"
        with open(registry_path, "w") as f:
            json.dump(
                {
                    "generated_at": datetime.utcnow().isoformat() + "Z",
                    "count": len(results),
                    "modules": self.registry,
                },
                f,
                indent=2,
            )
        return {"generated": len(results), "registry": str(registry_path)}
