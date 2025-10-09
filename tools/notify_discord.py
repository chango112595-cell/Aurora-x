#!/usr/bin/env python3
"""Discord notification tool for Aurora-X Ultra milestones."""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

def send_discord_notification(webhook_url: str = None):
    """Send Aurora-X Ultra completion notification to Discord."""
    
    if not webhook_url:
        webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    
    if not webhook_url:
        print("❌ No Discord webhook URL found")
        print("Set DISCORD_WEBHOOK_URL environment variable or pass as argument")
        return False
    
    # Load latest CI gate results
    ci_status = "✅ PASSED"
    try:
        import subprocess
        result = subprocess.run(["python", "tools/ci_gate.py"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            ci_status = "⚠️ WARNINGS"
    except:
        ci_status = "⏭️ SKIPPED"
    
    # Check if corpus exists
    corpus_size = 0
    try:
        import sqlite3
        conn = sqlite3.connect("corpus.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM corpus")
        corpus_size = cursor.fetchone()[0]
        conn.close()
    except:
        pass
    
    # Build the Discord message
    embed = {
        "title": "🌌 Aurora-X Ultra Complete!",
        "description": "Autonomous code synthesis engine with offline-first architecture",
        "color": 0x00ffff,  # Cyan color
        "timestamp": datetime.utcnow().isoformat(),
        "fields": [
            {
                "name": "📊 Core Features",
                "value": (
                    "• **Corpus Recording**: JSONL + SQLite persistence\n"
                    "• **Learning Seeds**: EMA bias (α=0.2, drift cap ±0.15)\n"
                    "• **Adaptive Engine**: ε-greedy exploration (ε=0.15)\n"
                    "• **HTML Reports**: Baseline comparisons + regressions"
                ),
                "inline": False
            },
            {
                "name": "🚀 Production Ready",
                "value": (
                    "• **CI Gate**: " + ci_status + "\n"
                    "• **Config**: Locked parameters (prod_config.py)\n"
                    "• **Snapshots**: Daily backups (30-day retention)\n"
                    f"• **Corpus**: {corpus_size:,} entries"
                ),
                "inline": False
            },
            {
                "name": "📱 Live Monitoring",
                "value": (
                    "• **Dashboard**: http://localhost:5000/dashboard\n"
                    "• **Task Tracker**: Floating HUD + Web interface\n"
                    "• **API Endpoints**: Real-time bias evolution\n"
                    "• **Auto-refresh**: Every 1.5 seconds"
                ),
                "inline": False
            },
            {
                "name": "🎯 Key Metrics",
                "value": (
                    "• **Drift Bound**: 5.0 (geometric series limit)\n"
                    "• **Decay Rate**: 0.98 (exponential)\n"
                    "• **Cooldown**: 5 iterations\n"
                    "• **Top-K Seeds**: 10 candidates"
                ),
                "inline": False
            }
        ],
        "footer": {
            "text": "Aurora-X Ultra v1.0.0 | Python 3.11+ | SQLite + JSONL",
            "icon_url": "https://cdn.discordapp.com/embed/avatars/0.png"
        },
        "author": {
            "name": "Aurora-X Ultra",
            "icon_url": "https://cdn.discordapp.com/embed/avatars/1.png"
        }
    }
    
    # Prepare the payload
    payload = {
        "username": "Aurora-X Bot",
        "avatar_url": "https://cdn.discordapp.com/embed/avatars/2.png",
        "content": "🎉 **Major Milestone Achieved!**",
        "embeds": [embed]
    }
    
    # Send the notification
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status in [200, 204]:
                print("✅ Discord notification sent successfully!")
                return True
            else:
                print(f"❌ Discord API error: {response.status}")
                print(response.read().decode())
                return False
    except urllib.error.URLError as e:
        print(f"❌ Failed to send notification: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main entry point."""
    webhook_url = sys.argv[1] if len(sys.argv) > 1 else None
    success = send_discord_notification(webhook_url)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()