import os
from dataclasses import dataclass

SUPPORTED = ("python", "go", "rust", "csharp")


@dataclass
class LangChoice:
    lang: str
    reason: str


def _env_override():
    v = os.getenv("AURORA_DEFAULT_LANG", "").strip().lower()
    return v if v in SUPPORTED else None


def pick_language(user_text: str) -> LangChoice:
    env = _env_override()
    if env:
        return LangChoice(env, f"env override AURORA_DEFAULT_LANG={env}")
    t = (user_text or "").lower()
    if any(k in t for k in ["fast", "high performance", "microservice", "api service", "concurrency"]) and "web" in t:
        return LangChoice("go", "fast web service → go")
    if any(k in t for k in ["memory-safe", "systems", "cli", "binary", "performance"]) and "cli" in t:
        return LangChoice("rust", "memory-safe cli → rust")
    if any(k in t for k in ["enterprise", "windows", "asp.net", "web api", "api controller"]):
        return LangChoice("csharp", "enterprise web api → csharp")
    return LangChoice("python", "default → python")
