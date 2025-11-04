import socket
import json
from datetime import datetime

def check_aurora():
    """Quick Aurora health check"""
    ports = {
        5000: "Aurora UI",
        5002: "Learning API", 
        8000: "Dashboards"
    }
    
    print("\n" + "="*60)
    print("🤖 AURORA-X SYSTEM STATUS")
    print("="*60 + "\n")
    
    all_up = True
    results = {}
    
    for port, service in ports.items():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            s.connect(("127.0.0.1", port))
            s.close()
            status = "✅ ONLINE"
            results[port] = True
        except:
            status = "❌ OFFLINE"
            results[port] = False
            all_up = False
        
        print(f"  [{port}] {service:20} → {status}")
    
    print("\n" + "="*60)
    
    if all_up:
        print("✨ Aurora is FULLY OPERATIONAL")
        print("\n📍 Access Points:")
        print("   • UI Dashboard: http://127.0.0.1:5000")
        print("   • Dashboards:   http://127.0.0.1:8000")
        print("   • Learning API: http://127.0.0.1:5002")
    else:
        print("⚠️  Aurora has OFFLINE SERVICES")
        down = [p for p,u in results.items() if not u]
        print(f"\n   Offline: {down}")
    
    print("="*60 + "\n")
    
    return all_up

if __name__ == "__main__":
    check_aurora()
