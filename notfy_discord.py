import json
import os
import urllib.request

URL = os.getenv("DISCORD_WEBHOOK_URL")

def send(msg: str):
    if not URL:
        print("❌ No DISCORD_WEBHOOK_URL found")
        return
    data = json.dumps({"content": msg}).encode("utf-8")
    req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req)
    print("✅ Sent:", msg)

if __name__ == "__main__":
    send("✅ Aurora-X notifier wired successfully!")
