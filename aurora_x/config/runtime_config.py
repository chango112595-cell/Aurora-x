"""Runtime configuration validation and dependency checks for Aurora-X.

- Validates required secrets and configuration at startup
- Detects optional dependencies and exposes readiness summary
- Provides data root helper for file-based state
"""

import importlib.util
import logging
import os
import time
from pathlib import Path
from typing import Any

REQUIRED_SECRETS = ["AURORA_TOKEN_SECRET"]
OPTIONAL_DEP_KEYS = [
    "AURORA_API_KEY",
    "AURORA_LLM_ENDPOINT",
    "CAN_CHANNEL",
    "CAN_BUSTYPE",
    "UDS_RX_ID",
    "UDS_TX_ID",
    "MAVLINK_CONNECTION",
]

OPTIONAL_DEP_MODULES = {
    "aiortc": "WebRTC peer connections",
    "aiohttp": "WebRTC signaling server",
    "can": "CAN bus interface",
    "udsoncan": "UDS ECU diagnostics",
    "pymavlink": "MAVLink flight telemetry",
    "requests": "HTTP client for local LLM endpoint",
}

_DATA_ROOT_ENV = "AURORA_DATA_ROOT"
_DEFAULT_DATA_ROOT = Path("data")

_LOG = logging.getLogger(__name__)


def data_root() -> Path:
    """Resolve the data root path (configurable via AURORA_DATA_ROOT)."""
    root = Path(os.environ.get(_DATA_ROOT_ENV, _DEFAULT_DATA_ROOT))
    root.mkdir(parents=True, exist_ok=True)
    return root


def data_path(*parts: str) -> Path:
    """Build a path under the data root."""
    return data_root().joinpath(*parts)


def _check_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def dependency_status() -> dict[str, dict[str, Any]]:
    """Return availability of optional dependencies."""
    status: dict[str, dict[str, Any]] = {}
    for mod, purpose in OPTIONAL_DEP_MODULES.items():
        available = _check_module(mod)
        status[mod] = {"available": available, "purpose": purpose}
    return status


def validate_required_config() -> dict[str, Any]:
    """Validate required secrets/config. Raises on missing.

    Returns a summary dict for readiness reporting.
    """
    allow_missing = os.environ.get("AURORA_ALLOW_MISSING_SECRETS", "").lower() in {
        "1",
        "true",
        "yes",
    }

    missing = [key for key in REQUIRED_SECRETS if not os.environ.get(key)]
    summary = {
        "missing": missing,
        "checked_at": time.time(),
        "required": REQUIRED_SECRETS,
    }
    if missing and not allow_missing:
        raise RuntimeError(f"Missing required secrets: {', '.join(missing)}")
    return summary


def readiness() -> dict[str, Any]:
    """Build readiness summary including deps and config."""
    try:
        cfg = validate_required_config()
        config_ok = True
    except Exception as exc:  # keep message for health reporting (internally)
        # Log full exception details server-side, but avoid exposing them in the response.
        _LOG.exception("Configuration validation failed during readiness check")
        missing = getattr(exc, "missing", [])
        cfg = {
            "error": "configuration validation failed",
            "missing": missing,
            "missing_count": len(missing),
        }
        config_ok = False

    deps = dependency_status()
    unavailable = [k for k, v in deps.items() if not v["available"]]
    return {
        "config_ok": config_ok,
        "config": cfg,
        "dependencies": deps,
        "dependencies_available": len(unavailable) == 0,
        "unavailable_dependencies": unavailable,
    }
