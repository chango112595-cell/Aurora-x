#!/usr/bin/env python3
"""
Message Relay to Aurora
Copilot supervises and relays user messages to Aurora's debugging system
"""
import json
import time
from datetime import datetime
from pathlib import Path

def relay_debug_message():
    """Relay debug request to Aurora"""
    
    print("📡 Copilot: Relaying debug request to Aurora...")
    
    # Create message for Aurora's debugging system
    message = {
        "timestamp": datetime.now().isoformat(),
        "from": "USER_VIA_COPILOT",
        "message": "User requests Aurora to debug current issue",
        "context": "Blank pages still occurring, need Aurora to run full diagnostic",
        "urgency": "HIGH",
        "action_required": "AUTONOMOUS_DEBUG"
    }
    
    # Write to Aurora's message queue
    aurora_messages = Path("/workspaces/Aurora-x/.aurora_knowledge/debug_requests.jsonl")
    aurora_messages.parent.mkdir(exist_ok=True)
    
    with open(aurora_messages, "a") as f:
        f.write(json.dumps(message) + "\n")
    
    print("✅ Copilot: Message delivered to Aurora's debug queue")
    
    # Trigger Aurora's Luminar Nexus to check for new debug requests
    try:
        import subprocess
        
        # Check if Aurora's systems are running
        result = subprocess.run(['pgrep', '-f', 'luminar'], capture_output=True, text=True)
        
        if result.stdout:
            print("✅ Copilot: Aurora's Luminar Nexus is running - she should receive the debug request")
        else:
            print("⚠️ Copilot: Aurora's Luminar Nexus not detected - starting emergency debug mode")
            
            # Emergency: directly call Aurora's debug system
            subprocess.Popen([
                'python', 
                '/workspaces/Aurora-x/tools/aurora_emergency_debug.py'
            ])
            
    except Exception as e:
        print(f"⚠️ Copilot: Error contacting Aurora - {e}")
    
    print("\n🌟 Aurora should now be debugging the issue...")
    print("📊 Monitoring Aurora's response...")
    
    # Monitor for Aurora's response
    monitor_aurora_response()

def monitor_aurora_response():
    """Monitor Aurora's debug response"""
    response_file = Path("/workspaces/Aurora-x/.aurora_knowledge/debug_responses.jsonl")
    
    print("👁️ Copilot: Waiting for Aurora's response (30 seconds max)...")
    
    start_time = time.time()
    while time.time() - start_time < 30:
        if response_file.exists():
            with open(response_file, "r") as f:
                lines = f.readlines()
                if lines:
                    latest = json.loads(lines[-1])
                    print(f"🌟 Aurora responded: {latest.get('message', 'Debug in progress')}")
                    if latest.get('status') == 'COMPLETE':
                        print("✅ Copilot: Aurora completed debugging")
                        return
        
        time.sleep(2)
        print("⏳ Copilot: Still waiting for Aurora...")
    
    print("⚠️ Copilot: Aurora didn't respond within 30 seconds")
    print("📋 Copilot: Aurora may be working on complex debugging - check her logs")

if __name__ == "__main__":
    relay_debug_message()