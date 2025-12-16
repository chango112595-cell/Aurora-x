#!/usr/bin/env python3
"""
Aurora Phase-1 Production Module Generator
Generates init, execute, and cleanup files for each module in manifest.
"""
import json
import argparse
import os
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent

MODULE_TEMPLATES = {
    "connector": {
        "init": '''
class {class_name}Init:
    """Initialize {name} connector with driver: {driver}"""
    
    def __init__(self, config=None):
        self.config = config or {{}}
        self.connection = None
        self.connected = False
        self.driver = "{driver}"
        self.timeout = self.config.get("timeout_ms", 30000)
        self.retry_count = self.config.get("retry_count", 3)
    
    def init(self):
        """Initialize the connector resources"""
        try:
            self.connection = self._create_connection()
            self.connected = True
            return {{"status": "initialized", "driver": self.driver}}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}
    
    def _create_connection(self):
        return {{"type": self.driver, "state": "ready", "buffer": []}}

def init(config=None):
    instance = {class_name}Init(config)
    return instance.init()
''',
        "execute": '''
import time

class {class_name}Execute:
    """Execute {name} connector operations"""
    
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}
        self.connection = self.ctx.get("connection")
        self.driver = "{driver}"
    
    def execute(self, payload):
        start = time.time()
        try:
            endpoint = payload.get("endpoint", "default")
            data = payload.get("data", {{}})
            method = payload.get("method", "GET")
            
            response = self._send_request(endpoint, data, method)
            duration = (time.time() - start) * 1000
            
            return {{
                "status": "ok",
                "driver": self.driver,
                "endpoint": endpoint,
                "response": response,
                "duration_ms": duration
            }}
        except Exception as e:
            return {{"status": "error", "error": str(e), "duration_ms": (time.time() - start) * 1000}}
    
    def _send_request(self, endpoint, data, method):
        return {{"received": True, "endpoint": endpoint, "method": method, "data_size": len(str(data))}}

def execute(payload=None):
    instance = {class_name}Execute()
    return instance.execute(payload or {{}})
''',
        "cleanup": '''
class {class_name}Cleanup:
    """Cleanup {name} connector resources"""
    
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}
        self.connection = self.ctx.get("connection")
    
    def cleanup(self):
        try:
            if self.connection:
                self.connection = None
            return {{"status": "cleaned", "resources_freed": True}}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}

def cleanup(ctx=None):
    instance = {class_name}Cleanup(ctx)
    return instance.cleanup()
'''
    },
    "processor": {
        "init": '''
class {class_name}Init:
    """Initialize {name} processor with mode: {driver}"""
    
    def __init__(self, config=None):
        self.config = config or {{}}
        self.mode = "{driver}"
        self.buffer = []
        self.batch_size = self.config.get("batch_size", 100)
    
    def init(self):
        self.buffer = []
        return {{"status": "initialized", "mode": self.mode, "batch_size": self.batch_size}}

def init(config=None):
    instance = {class_name}Init(config)
    return instance.init()
''',
        "execute": '''
import time

class {class_name}Execute:
    """Execute {name} processor operations"""
    
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}
        self.mode = "{driver}"
        self.buffer = self.ctx.get("buffer", [])
    
    def execute(self, payload):
        start = time.time()
        try:
            data = payload.get("data", [])
            operation = payload.get("operation", "transform")
            
            if self.mode == "batch":
                result = self._process_batch(data, operation)
            elif self.mode == "stream":
                result = self._process_stream(data, operation)
            elif self.mode == "parallel":
                result = self._process_parallel(data, operation)
            else:
                result = self._process_sequential(data, operation)
            
            return {{"status": "ok", "result": result, "duration_ms": (time.time() - start) * 1000}}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}
    
    def _process_batch(self, data, operation):
        return {{"processed": len(data) if isinstance(data, list) else 1, "mode": "batch", "operation": operation}}
    
    def _process_stream(self, data, operation):
        return {{"processed": 1, "mode": "stream", "buffered": True}}
    
    def _process_parallel(self, data, operation):
        return {{"processed": len(data) if isinstance(data, list) else 1, "mode": "parallel", "workers": 4}}
    
    def _process_sequential(self, data, operation):
        return {{"processed": len(data) if isinstance(data, list) else 1, "mode": "sequential"}}

def execute(payload=None):
    instance = {class_name}Execute()
    return instance.execute(payload or {{}})
''',
        "cleanup": '''
class {class_name}Cleanup:
    """Cleanup {name} processor resources"""
    
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}
        self.buffer = self.ctx.get("buffer", [])
    
    def cleanup(self):
        self.buffer.clear() if hasattr(self.buffer, 'clear') else None
        return {{"status": "cleaned", "buffer_cleared": True}}

def cleanup(ctx=None):
    instance = {class_name}Cleanup(ctx)
    return instance.cleanup()
'''
    },
    "analyzer": {
        "init": '''
class {class_name}Init:
    """Initialize {name} analyzer with strategy: {driver}"""
    
    def __init__(self, config=None):
        self.config = config or {{}}
        self.strategy = "{driver}"
        self.patterns = []
        self.threshold = self.config.get("threshold", 0.8)
    
    def init(self):
        self.patterns = self._load_patterns()
        return {{"status": "initialized", "strategy": self.strategy, "patterns_loaded": len(self.patterns)}}
    
    def _load_patterns(self):
        return ["pattern_1", "pattern_2", "pattern_3"]

def init(config=None):
    instance = {class_name}Init(config)
    return instance.init()
''',
        "execute": '''
import time
import re

class {class_name}Execute:
    """Execute {name} analyzer operations"""
    
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}
        self.strategy = "{driver}"
        self.patterns = self.ctx.get("patterns", [])
        self.threshold = self.ctx.get("threshold", 0.8)
    
    def execute(self, payload):
        start = time.time()
        try:
            data = payload.get("data", "")
            target = payload.get("target", "content")
            
            if self.strategy == "pattern":
                result = self._analyze_patterns(data)
            elif self.strategy == "statistical":
                result = self._analyze_statistical(data)
            elif self.strategy == "ml":
                result = self._analyze_ml(data)
            else:
                result = self._analyze_rules(data)
            
            return {{"status": "ok", "analysis": result, "duration_ms": (time.time() - start) * 1000}}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}
    
    def _analyze_patterns(self, data):
        matches = []
        text = str(data)
        for p in self.patterns:
            if p in text:
                matches.append(p)
        return {{"matches": matches, "score": len(matches) / max(len(self.patterns), 1)}}
    
    def _analyze_statistical(self, data):
        text = str(data)
        return {{"length": len(text), "words": len(text.split()), "score": min(len(text) / 1000, 1.0)}}
    
    def _analyze_ml(self, data):
        return {{"prediction": "normal", "confidence": 0.95, "model": "aurora-v1"}}
    
    def _analyze_rules(self, data):
        return {{"rules_checked": 10, "passed": 9, "failed": 1, "score": 0.9}}

def execute(payload=None):
    instance = {class_name}Execute()
    return instance.execute(payload or {{}})
''',
        "cleanup": '''
class {class_name}Cleanup:
    """Cleanup {name} analyzer resources"""
    
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}
    
    def cleanup(self):
        return {{"status": "cleaned", "patterns_unloaded": True}}

def cleanup(ctx=None):
    instance = {class_name}Cleanup(ctx)
    return instance.cleanup()
'''
    }
}

DEFAULT_TEMPLATE = {
    "init": '''
class {class_name}Init:
    """Initialize {name} module with driver: {driver}"""
    
    def __init__(self, config=None):
        self.config = config or {{}}
        self.driver = "{driver}"
        self.initialized = False
    
    def init(self):
        self.initialized = True
        return {{"status": "initialized", "driver": self.driver, "category": "{category}"}}

def init(config=None):
    instance = {class_name}Init(config)
    return instance.init()
''',
    "execute": '''
import time

class {class_name}Execute:
    """Execute {name} module operations"""
    
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}
        self.driver = "{driver}"
    
    def execute(self, payload):
        start = time.time()
        try:
            action = payload.get("action", "default")
            data = payload.get("data", {{}})
            
            result = self._process(action, data)
            
            return {{
                "status": "ok",
                "action": action,
                "result": result,
                "duration_ms": (time.time() - start) * 1000
            }}
        except Exception as e:
            return {{"status": "error", "error": str(e), "duration_ms": (time.time() - start) * 1000}}
    
    def _process(self, action, data):
        return {{"processed": True, "action": action, "input_size": len(str(data))}}

def execute(payload=None):
    instance = {class_name}Execute()
    return instance.execute(payload or {{}})
''',
    "cleanup": '''
class {class_name}Cleanup:
    """Cleanup {name} module resources"""
    
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}
    
    def cleanup(self):
        return {{"status": "cleaned", "resources_freed": True}}

def cleanup(ctx=None):
    instance = {class_name}Cleanup(ctx)
    return instance.cleanup()
'''
}


def get_template(category: str) -> dict:
    return MODULE_TEMPLATES.get(category, DEFAULT_TEMPLATE)


def generate_module_file(template: str, module: dict, file_type: str) -> str:
    class_name = f"{module['category'].title()}_{module['id']}"
    
    header = f'''"""
Aurora Module: {module['name']}
ID: {module['id']}
Category: {module['category']}
Driver: {module['driver']}
Type: {file_type}
Generated: {datetime.now(timezone.utc).isoformat()}
"""
'''
    
    code = template.format(
        class_name=class_name,
        name=module['name'],
        driver=module['driver'],
        category=module['category'],
        id=module['id']
    )
    
    return header + code.strip()


def generate_module(module: dict, output_dir: Path, force: bool = False) -> dict:
    category_dir = output_dir / module['category']
    category_dir.mkdir(parents=True, exist_ok=True)
    
    template = get_template(module['category'])
    files_generated = []
    
    for file_type in ['init', 'execute', 'cleanup']:
        filename = f"{module['category']}_{module['id']}_{file_type}.py"
        filepath = category_dir / filename
        
        if filepath.exists() and not force:
            continue
        
        content = generate_module_file(template[file_type], module, file_type)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        files_generated.append(str(filepath))
    
    return {
        "module_id": module['id'],
        "category": module['category'],
        "files": files_generated
    }


def generate_all_modules(manifest_path: str, output_dir: str, force: bool = False) -> dict:
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    results = []
    total = len(manifest['modules'])
    
    for i, module in enumerate(manifest['modules'], 1):
        result = generate_module(module, output_path, force)
        results.append(result)
        
        if i % 50 == 0 or i == total:
            print(f"[GENERATE] Progress: {i}/{total} modules")
    
    registry = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "total_modules": len(results),
        "output_dir": str(output_path),
        "modules": {r['module_id']: r for r in results}
    }
    
    registry_path = output_path / "modules_registry.json"
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)
    
    return {
        "total": len(results),
        "output_dir": str(output_path),
        "registry": str(registry_path),
        "results": results
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate Aurora modules from manifest"
    )
    parser.add_argument(
        "--manifest", "-m",
        type=str,
        required=True,
        help="Path to manifest file"
    )
    parser.add_argument(
        "--out", "-o",
        type=str,
        default="generated_modules",
        help="Output directory for generated modules"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Overwrite existing files"
    )
    
    args = parser.parse_args()
    
    print(f"[GENERATE] Loading manifest: {args.manifest}")
    print(f"[GENERATE] Output directory: {args.out}")
    
    result = generate_all_modules(args.manifest, args.out, args.force)
    
    print(f"[GENERATE] Generated {result['total']} modules")
    print(f"[GENERATE] Registry: {result['registry']}")
    
    return result


if __name__ == "__main__":
    main()
