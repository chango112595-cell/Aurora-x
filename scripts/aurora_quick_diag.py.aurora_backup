
#!/usr/bin/env python3
"""
Aurora Server Diagnostic Tool
Cross-platform port and process checker
"""

import socket
import subprocess
import sys
import platform

def print_header(text):
    print(f"\n{'='*50}")
    print(f"  {text}")
    print(f"{'='*50}\n")

def check_port(port):
    """Check if a port is in use"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('0.0.0.0', port))
    sock.close()
    return result == 0

def get_process_on_port(port):
    """Try to identify process on port"""
    system = platform.system()
    try:
        if system == "Linux" or system == "Darwin":
            result = subprocess.run(
                ['lsof', '-i', f':{port}', '-sTCP:LISTEN'],
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        elif system == "Windows":
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True,
                text=True
            )
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    return line.strip()
    except:
        pass
    return None

def main():
    print_header("AURORA SERVER DIAGNOSTIC REPORT")
    
    # Critical ports to check
    ports = {
        5000: "Express Backend (Main)",
        8000: "Luminar Nexus V2",
        8100: "Alternative Python Backend",
        9000: "Alternative Python Backend",
        3000: "Vite Dev Server (if separate)",
    }
    
    print("▶ Checking Critical Ports...\n")
    
    active_ports = []
    for port, description in ports.items():
        is_active = check_port(port)
        status = "✔ ACTIVE" if is_active else "✘ INACTIVE"
        color = "\033[92m" if is_active else "\033[91m"
        reset = "\033[0m"
        
        print(f"{color}{status}{reset} Port {port}: {description}")
        
        if is_active:
            active_ports.append(port)
            process_info = get_process_on_port(port)
            if process_info:
                print(f"  └─ {process_info}")
    
    print_header("SUMMARY")
    
    if 5000 in active_ports:
        print("✔ Express backend is running on port 5000")
    else:
        print("✘ WARNING: Express backend NOT detected on port 5000")
    
    if 8000 in active_ports:
        print("✔ Luminar Nexus V2 is running on port 8000")
    else:
        print("⚠ Luminar Nexus V2 NOT detected on port 8000")
    
    print(f"\n📊 Total active ports: {len(active_ports)}")
    print(f"🔧 Platform: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version.split()[0]}\n")

if __name__ == "__main__":
    main()
