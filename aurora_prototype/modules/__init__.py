from .hello import HelloModule
from .add import AddModule

MODULES = {
    "hello": HelloModule(),
    "add": AddModule(),
}

__all__ = ["MODULES"]
