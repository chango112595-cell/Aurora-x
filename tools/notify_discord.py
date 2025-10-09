#!/usr/bin/env python3
"""Discord notification tool for Aurora-X Ultra."""

import os, json, urllib.request, urllib.error

URL = os.getenv("DISCORD_WEBHOOK_URL")

def send(msg: str):
    if not URL:
        print("❌ No DISCORD_WEBHOOK_URL found")
        return False
    
    try:
        data = json.dumps({"content": msg}).encode("utf-8")
        req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status in [200, 204]:
                print("✅ Sent:", msg)
                return True
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}")
        if e.code == 403:
            print("⚠️  Check if webhook URL is valid and not expired")
    except urllib.error.URLError as e:
        print(f"❌ Connection Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    return False

if __name__ == "__main__":
    send("✅ Aurora-X notifier wired successfully!")