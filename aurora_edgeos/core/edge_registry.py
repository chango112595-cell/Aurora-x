class EdgeRegistry:
    def __init__(self, device_id):
        self.device_id = device_id
        self.data = {
            "id": device_id,
            "capabilities": {},
            "sensors": {},
            "actuators": {}
        }

    def register_capability(self, name, value=True):
        self.data["capabilities"][name] = value

    def register_sensor(self, name, metadata):
        self.data["sensors"][name] = metadata

    def register_actuator(self, name, metadata):
        self.data["actuators"][name] = metadata

    def export(self):
        return self.data
