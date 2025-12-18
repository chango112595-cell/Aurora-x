class Actuator:
    def __init__(self, name, set_fn):
        self.name = name
        self.set_fn = set_fn

    def activate(self, value):
        return self.set_fn(value)
