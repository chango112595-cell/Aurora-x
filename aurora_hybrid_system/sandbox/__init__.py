from .sandbox_pure.pure_sandbox import PureSandbox
from .sandbox_hybrid.hybrid_sandbox import HybridSandbox

def get_sandbox(mode="hybrid", **kwargs):
    if mode == "pure":
        return PureSandbox(**kwargs)
    return HybridSandbox(**kwargs)
