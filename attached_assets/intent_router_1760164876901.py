
from dataclasses import dataclass
import re

@dataclass
class Intent:
    kind: str           # 'web_app' | 'cli_tool' | 'lib_func'
    name: str
    brief: str
    fields: dict

def _slug(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s.strip().lower()).strip("_")
    return s or "app"

def classify(text: str) -> Intent:
    t = (text or "").strip().lower()
    if any(k in t for k in ["ui", "web", "page", "site", "dashboard", "timer", "countdown"]):
        feature = "timer" if ("timer" in t or "countdown" in t) else "web"
        return Intent(kind="web_app", name=_slug("timer_ui" if feature=="timer" else t[:28]), brief=text.strip(), fields={"feature": feature})
    if any(k in t for k in ["cli", "script", "tool"]):
        return Intent(kind="cli_tool", name=_slug(t[:28] or "tool"), brief=text.strip(), fields={})
    return Intent(kind="lib_func", name=_slug(t[:28] or "function"), brief=text.strip(), fields={})
