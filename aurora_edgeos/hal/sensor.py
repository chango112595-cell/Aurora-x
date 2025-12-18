class Sensor:
    def __init__(self, name, read_fn):
        self.name = name
        self.read_fn = read_fn

    def read(self):
        return self.read_fn()
