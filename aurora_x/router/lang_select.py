import os
import re
from dataclasses import dataclass

SUPPORTED = ("python", "go", "rust", "csharp")

@dataclass
class LangChoice:
    lang: str
    reason: str

def _env_override() -> str | None:
    """Check for environment variable override."""
    v = os.getenv("AURORA_DEFAULT_LANG", "").strip().lower()
    return v if v in SUPPORTED else None

def pick_language(user_text: str) -> LangChoice:
    """
    Automatically select the best programming language based on prompt keywords.
    
    Decision tree:
    1. Environment override (AURORA_DEFAULT_LANG)
    2. Go: fast, microservice, high performance + web context
    3. Rust: memory-safe, systems, CLI, binary
    4. C#: enterprise, Windows, ASP.NET, web API
    5. Python: default fallback for everything else
    """
    # Check for environment override first
    env = _env_override()
    if env:
        return LangChoice(env, f"env override AURORA_DEFAULT_LANG={env}")
    
    t = (user_text or "").lower()
    
    # Go: High-performance web services and microservices
    if any(k in t for k in ["fast", "high performance", "microservice", "api service", "concurrency", "golang", "go"]):
        if any(w in t for w in ["web", "api", "service", "server", "http"]):
            return LangChoice("go", "fast web service/microservice → Go")
    
    # Rust: Memory-safe system tools and CLIs
    if any(k in t for k in ["memory-safe", "memory safe", "systems", "rust", "cargo", "binary", "performance"]):
        if any(c in t for c in ["cli", "command", "tool", "parser"]):
            return LangChoice("rust", "memory-safe CLI/systems → Rust")
    
    # C#: Enterprise and Windows-focused APIs
    if any(k in t for k in ["enterprise", "windows", "asp.net", "dotnet", ".net", "c#", "csharp", "api controller"]):
        return LangChoice("csharp", "enterprise/Windows API → C#")
    
    # Python: Default for everything else
    return LangChoice("python", "default → Python")