"""pack08_conversational_engine core.module - production implementation"""

import json
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
LOGS = DATA / "logs"
CONV = DATA / "conversations.jsonl"
for p in (DATA, LOGS):
    p.mkdir(parents=True, exist_ok=True)


def _log_event(event: dict[str, Any]) -> None:
    event.setdefault("ts", time.time())
    with CONV.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def info():
    return {"pack": "pack08_conversational_engine", "version": "1.0.0", "ts": time.time()}


def health_check():
    try:
        heartbeat = DATA / "health.touch"
        heartbeat.write_text(str(time.time()))
        return True
    except Exception:
        return False


def initialize():
    """Initialize the pack module."""
    print("[pack08_conversational_engine] Initializing...")
    DATA.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    return True


def shutdown():
    """Gracefully shutdown the pack module."""
    print("[pack08_conversational_engine] Shutting down...")
    return True


def _classify_intent(message: str) -> str:
    text = message.lower()
    if any(k in text for k in ["help", "how", "what"]):
        return "info"
    if any(k in text for k in ["error", "fail", "issue"]):
        return "diagnostic"
    if any(k in text for k in ["run", "execute", "do"]):
        return "action"
    return "chat"


def _respond(message: str, context: list[dict[str, Any]]) -> str:
    summary = ""
    if context:
        last = context[-1].get("message", "")
        summary = f" (noted previous: {last[:60]})"
    return f"Aurora received: '{message}'. Intent captured{summary}."


def execute(command: str, params: dict = None):
    """
    Execute a command within this pack.
    Supported commands:
      - chat: {message, context?}
      - classify: {message}
      - remember: {message, meta?}
      - recall: {limit?}
    """
    params = params or {}
    if not command:
        return {"status": "error", "error": "command required", "ts": time.time()}

    history = list(load_recent(limit=10))

    if command == "classify":
        message = params.get("message", "")
        intent = _classify_intent(message)
        _log_event({"type": "classify", "message": message, "intent": intent})
        return {"status": "ok", "intent": intent, "ts": time.time()}

    if command == "chat":
        message = params.get("message", "")
        intent = _classify_intent(message)
        reply = _respond(message, history)
        event = {"type": "chat", "message": message, "intent": intent, "reply": reply}
        _log_event(event)
        return {"status": "ok", "reply": reply, "intent": intent, "ts": time.time()}

    if command == "remember":
        message = params.get("message", "")
        meta = params.get("meta", {})
        _log_event({"type": "memory", "message": message, "meta": meta})
        return {"status": "ok", "stored": True, "ts": time.time()}

    if command == "recall":
        limit = int(params.get("limit", 5))
        return {"status": "ok", "items": history[:limit], "ts": time.time()}

    # default passthrough for compatibility with existing tests
    _log_event({"type": "command", "command": command, "params": params})
    return {"status": "ok", "command": command, "params": params, "ts": time.time()}


def load_recent(limit: int = 5):
    if not CONV.exists():
        return []
    items = []
    with CONV.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                items.append(json.loads(line))
            except Exception:
                continue
    return list(reversed(items))[:limit]
