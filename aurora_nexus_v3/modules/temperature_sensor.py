import random
import time


class TemperatureSensor:
    def __init__(self):
        self.offset = 0.0

    def read(self) -> float:
        t = time.time()
        val = 22.0 + (t % 5) + (random.random() - 0.5) * 0.2 + self.offset
        return round(val, 2)
