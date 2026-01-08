import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


class AuroraHybridCore:
    def __init__(self, base_dir="aurora_data"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        from autonomy import AutonomyEngine
        from bridge import AuroraBridge
        from inspector import StaticInspector
        from lifecycle import ModuleLifecycle
        from module_generator import ModuleGenerator
        from registry import ModuleRegistry
        from rule_engine import CapabilityManager, RuleEngine
        from sandbox import get_sandbox
        from security import SecurityLayer
        from tester import AutonomousTester
        from workers import WorkerPool

        self.sandbox_pure = get_sandbox("pure")
        self.sandbox_hybrid = get_sandbox("hybrid")
        self.autonomy = AutonomyEngine(str(self.base_dir / "autonomy"))
        self.tester = AutonomousTester(max_workers=100)
        self.inspector = StaticInspector()
        self.generator = ModuleGenerator(str(self.base_dir / "generated_modules"))
        self.rule_engine = RuleEngine()
        self.capability_mgr = CapabilityManager()
        self.lifecycle = ModuleLifecycle()
        self.security = SecurityLayer()
        self.registry = ModuleRegistry(str(self.base_dir / "registry.json"))
        self.worker_pool = WorkerPool(worker_count=100, hybrid_workers=200)
        self.bridge = AuroraBridge()
        logger.info("Aurora Hybrid Core initialized")

    def generate_modules(self, count=550):
        manifest = self.generator.generate_manifest(count)
        result = self.generator.generate_all(manifest)
        logger.info(f"Generated {result['generated']} modules")
        return result

    def test_module(self, module_path, payload=None):
        return self.tester.test_module(module_path, payload)

    def inspect_module(self, module_path):
        return self.inspector.inspect(module_path)

    def handle_incident(self, module_path):
        return self.autonomy.handle_incident(module_path)

    def run_in_sandbox(self, code, mode="hybrid", payload=None):
        if mode == "pure":
            return self.sandbox_pure.run_code(code, payload)
        return self.sandbox_hybrid.run(code, payload)

    def get_status(self):
        return {
            "modules_registered": len(self.registry.modules),
            "workers": self.worker_pool.get_stats(),
            "bridge": self.bridge.get_status(),
        }

    def shutdown(self):
        self.worker_pool.shutdown()
        logger.info("Aurora Hybrid Core shutdown complete")
