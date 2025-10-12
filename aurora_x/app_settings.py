# aurora_x/app_settings.py
import os
from dataclasses import dataclass, field

def env_bool(name:str, default:bool) -> bool:
    v = os.getenv(name)
    return default if v is None else v.lower() in ("1","true","yes","on")

def env_int(name:str, default:int) -> int:
    try: return int(os.getenv(name, f"{default}"))
    except: return default

@dataclass
class UIThresholds:
    ok: int = 90
    warn: int = 60
    
    def __post_init__(self):
        self.ok = env_int("AURORA_UI_OK", self.ok)
        self.warn = env_int("AURORA_UI_WARN", self.warn)

@dataclass
class Settings:
    port: int = env_int("PORT", 8000)
    t08_enabled: bool = env_bool("AURORA_T08_ENABLED", True)
    ui: UIThresholds = field(default_factory=UIThresholds)

SETTINGS = Settings()