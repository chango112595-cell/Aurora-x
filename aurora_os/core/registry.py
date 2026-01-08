import json

from logging_system import AuroraLogger


class Registry:
    def __init__(self):
        self.logger = AuroraLogger("Registry")
        self.path = "aurora_os/config/registry.json"

        try:
            with open(self.path) as f:
                self.data = json.load(f)
        except:
            self.data = {}
            self.save()

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=4)

    def get(self, key):
        return self.data.get(key)

    def set(self, category, key, value):
        if category not in self.data:
            self.data[category] = {}
        self.data[category][key] = value
        self.save()

    def delete(self, category, key):
        try:
            del self.data[category][key]
            self.save()
        except KeyError:
            pass
