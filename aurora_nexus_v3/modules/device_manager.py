from typing import List


class DeviceManager:
    def __init__(self):
        self.devices = []

    def register(self, device_id: str):
        if device_id not in self.devices:
            self.devices.append(device_id)
            return True
        return False

    def list(self) -> List[str]:
        return list(self.devices)
