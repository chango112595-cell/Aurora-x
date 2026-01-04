from .add import AddModule
from .hello import HelloModule

MODULES = {
    "hello": HelloModule(),
    "add": AddModule(),
}

__all__ = ["MODULES"]
