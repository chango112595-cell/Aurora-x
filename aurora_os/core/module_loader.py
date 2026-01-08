import json

from logging_system import AuroraLogger


class ModuleLoader:
    def __init__(self, registry, process_manager):
        self.registry = registry
        self.process_manager = process_manager
        self.logger = AuroraLogger("ModuleLoader")

    def load_all_modules(self):
        with open("aurora_os/config/modules.json") as f:
            modules = json.load(f)

        self.registry.set("modules", None, modules)
        self.logger.info(f"Loaded {len(modules)} Aurora modules.")
