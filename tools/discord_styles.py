#!/usr/bin/env python3
"""Discord notification styles for Aurora-X Ultra."""

import os, json, urllib.request, urllib.error
from datetime import datetime

URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_embed(title: str, description: str, color: int, fields: list = None):
    """Send a rich Discord embed notification."""
    if not URL:
        print("❌ No DISCORD_WEBHOOK_URL found")
        return False
    
    embed = {
        "title": title,
        "description": description,
        "color": color,
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {
            "text": "Aurora-X Ultra",
            "icon_url": "https://cdn.discordapp.com/embed/avatars/1.png"
        }
    }
    
    if fields:
        embed["fields"] = fields
    
    payload = {
        "username": "Aurora-X Bot",
        "avatar_url": "https://cdn.discordapp.com/embed/avatars/2.png",
        "embeds": [embed]
    }
    
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status in [200, 204]:
                print(f"✅ Sent: {title}")
                return True
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}")
    except Exception as e:
        print(f"❌ Error: {e}")
    return False

def success(title: str, message: str, **kwargs):
    """Send a success notification (green)."""
    fields = [{"name": k.replace("_", " ").title(), "value": str(v), "inline": True} 
              for k, v in kwargs.items()]
    return send_embed(f"✅ {title}", message, 0x00ff00, fields)

def warning(title: str, message: str, **kwargs):
    """Send a warning notification (amber)."""
    fields = [{"name": k.replace("_", " ").title(), "value": str(v), "inline": True} 
              for k, v in kwargs.items()]
    return send_embed(f"⚠️ {title}", message, 0xffa500, fields)

def failure(title: str, message: str, **kwargs):
    """Send a failure notification (red)."""
    fields = [{"name": k.replace("_", " ").title(), "value": str(v), "inline": True} 
              for k, v in kwargs.items()]
    return send_embed(f"❌ {title}", message, 0xff0000, fields)

def milestone(title: str, message: str, **kwargs):
    """Send a milestone notification (cyan)."""
    fields = [{"name": k.replace("_", " ").title(), "value": str(v), "inline": True} 
              for k, v in kwargs.items()]
    return send_embed(f"🌌 {title}", message, 0x00ffff, fields)

if __name__ == "__main__":
    # Test all styles
    success("Test Success", "Everything is working perfectly!", iterations=100, score=0.95)
    warning("Drift Warning", "Bias drift approaching limits", current_drift=4.8, max_drift=5.0)
    failure("CI Gate Failed", "Production checks did not pass", failed_tests=3, total_tests=5)
    milestone("Synthesis Complete", "Aurora-X completed full synthesis run", functions=250, time="45m")