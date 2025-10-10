SAFE = "safe"
EXPLORE = "explore"
DEFAULT_MODE = SAFE
def is_safe(mode: str) -> bool:
    return (mode or DEFAULT_MODE).lower() == SAFE
