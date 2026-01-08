def probe():
    # pretend to detect hardware (USB, serial, etc.)
    return True


class ExampleDevice:
    def __init__(self, path=None):
        self.path = path

    def read(self):
        return {"sensor": 42}

    def write(self, payload):
        print("write", payload)


def open(path=None):
    return ExampleDevice(path=path)
