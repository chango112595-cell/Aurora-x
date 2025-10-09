#!/usr/bin/env python3
"""Discord notification tool for Aurora-X Ultra."""

import os, json, time, urllib.request, urllib.error
from typing import Optional, Dict, Any

WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")  # set in Replit/GitHub Secrets
USERNAME = os.getenv("DISCORD_USERNAME", "Aurora-X Bot")
AVATAR   = os.getenv("DISCORD_AVATAR",   "https://i.imgur.com/6kU3J0G.png")

# Brand colors
GREEN = 0x2ECC71; YELLOW = 0xF1C40F; RED = 0xE74C3C; BLUE = 0x3498DB; PURPLE = 0x8E44AD

def _post(payload: Dict[str, Any], retries: int = 3):
    if not WEBHOOK:
        print("❌ DISCORD_WEBHOOK_URL not set"); return False
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(WEBHOOK, data=data, headers={
        "Content-Type": "application/json",
        "User-Agent": "Aurora-X/1.0"  # Discord requires User-Agent header
    })
    for i in range(retries+1):
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return 200 <= r.status < 300
        except urllib.error.HTTPError as e:
            # Respect 429 rate limit
            if e.code == 429:
                retry_after = float(e.headers.get("Retry-After", "1.0"))
                time.sleep(min(5.0, retry_after))
                continue
            # transient 5xx
            if 500 <= e.code < 600 and i < retries:
                time.sleep(1.0 * (i+1)); continue
            print("❌ Discord HTTPError:", e); return False
        except Exception as e:
            if i < retries: time.sleep(1.0 * (i+1)); continue
            print("❌ Discord error:", e); return False

def send_text(msg: str) -> bool:
    return _post({"username": USERNAME, "avatar_url": AVATAR, "content": msg}) or False

def send_embed(title: str, description: str, color: int = BLUE, fields: Optional[list] = None, url: Optional[str] = None) -> bool:
    embed = {"title": title, "description": description, "color": color}
    if fields: embed["fields"] = fields
    if url: embed["url"] = url
    payload = {"username": USERNAME, "avatar_url": AVATAR, "embeds": [embed]}
    return _post(payload) or False

# Convenience styles
def success(msg: str, **kw) -> bool: return send_embed("✅ Success", msg, GREEN, **kw) or False
def warning(msg: str, **kw) -> bool: return send_embed("⚠️ Warning", msg, YELLOW, **kw) or False
def error(msg: str,   **kw) -> bool: return send_embed("❌ Failure", msg, RED, **kw) or False
def info(msg: str,    **kw) -> bool: return send_embed("ℹ️ Info", msg, BLUE, **kw) or False

# Domain-specific helpers
def commit_alert(repo: str, branch: str, commit_url: str, files: int, message: str) -> bool:
    return send_embed(
        "🚀 Commit pushed",
        f"`{repo}@{branch}`\n{message}",
        PURPLE,
        fields=[
            {"name":"Files", "value": str(files), "inline": True},
            {"name":"Link",  "value": commit_url or "(pending)", "inline": True},
        ],
        url=commit_url or None
    )

def snapshot_alert(path: str, kept: int) -> bool:
    return success(f"🗂️ Snapshot complete\n`{path}` (retained: {kept})")

def drift_warning(bias: str, value: float, cap: float) -> bool:
    return warning(f"Drift nearing cap for **{bias}**: `{value:.2f}` / `{cap:.2f}`")

def synthesis_report(iteration: int, wins: int, losses: int, top_summary: dict) -> bool:
    fields = [{"name":"Iteration","value":str(iteration),"inline":True},
              {"name":"Wins","value":str(wins),"inline":True},
              {"name":"Losses","value":str(losses),"inline":True}]
    summary = "\n".join(f"- `{k}`: {v:.3f}" for k,v in list(top_summary.items())[:10]) or "(no biases yet)"
    return send_embed("🧠 Synthesis Update", summary, BLUE, fields=fields)

if __name__ == "__main__":
    ok = success("Aurora-X notifier wired successfully ✨")
    print("Test sent:", ok)