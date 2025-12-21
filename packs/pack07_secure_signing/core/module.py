"""pack07_secure_signing core.module - production implementation."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Optional
import hmac
import json
import secrets
import time

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
KEY_PATH = DATA / "signing.key"
DATA.mkdir(parents=True, exist_ok=True)


def info():
    return {"pack": "pack07_secure_signing", "version": "1.0.0", "ts": time.time()}


def health_check():
    try:
        heartbeat = DATA / "health.touch"
        heartbeat.write_text(str(time.time()))
        return True
    except Exception:
        return False


def initialize():
    """Initialize the pack module."""
    print("[pack07_secure_signing] Initializing...")
    DATA.mkdir(parents=True, exist_ok=True)
    if not KEY_PATH.exists():
        _save_key(_generate_key())
    return True


def shutdown():
    """Gracefully shutdown the pack module."""
    print("[pack07_secure_signing] Shutting down...")
    return True


def _generate_key() -> str:
    return secrets.token_hex(32)


def _save_key(key: str) -> None:
    KEY_PATH.write_text(key)


def _load_key() -> str:
    if not KEY_PATH.exists():
        key = _generate_key()
        _save_key(key)
        return key
    return KEY_PATH.read_text().strip()


def sign_payload(payload: str, key: Optional[str] = None) -> str:
    key_bytes = (key or _load_key()).encode("utf-8")
    payload_bytes = payload.encode("utf-8")
    return hmac.new(key_bytes, payload_bytes, sha256).hexdigest()


def verify_signature(payload: str, signature: str, key: Optional[str] = None) -> bool:
    expected = sign_payload(payload, key=key)
    return hmac.compare_digest(expected, signature)


def fingerprint_key(key: Optional[str] = None) -> str:
    key_bytes = (key or _load_key()).encode("utf-8")
    return sha256(key_bytes).hexdigest()


def rotate_key() -> Dict[str, Any]:
    key = _generate_key()
    _save_key(key)
    return {"fingerprint": fingerprint_key(key), "rotated_at": time.time()}


def execute(command: str, params: dict = None):
    """Execute a command within this pack."""
    params = params or {}
    if command == "ensure_key":
        key = _load_key()
        return {"status": "ok", "fingerprint": fingerprint_key(key), "ts": time.time()}
    if command == "sign":
        payload = params.get("payload", "")
        signature = sign_payload(payload, params.get("key"))
        return {"status": "ok", "signature": signature, "ts": time.time()}
    if command == "verify":
        payload = params.get("payload", "")
        signature = params.get("signature", "")
        ok = verify_signature(payload, signature, params.get("key"))
        return {"status": "ok", "valid": ok, "ts": time.time()}
    if command == "fingerprint":
        return {"status": "ok", "fingerprint": fingerprint_key(params.get("key")), "ts": time.time()}
    if command == "rotate_key":
        return {"status": "ok", "rotation": rotate_key(), "ts": time.time()}
    return {"status": "ok", "command": command, "params": params, "ts": time.time()}
