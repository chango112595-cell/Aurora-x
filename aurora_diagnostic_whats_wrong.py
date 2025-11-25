"""
Aurora Deep Diagnostic - Find Out What's Going Wrong
User reports: Aurora is receiving messages but not responding
"""
import subprocess
import json
import time
import requests
from pathlib import Path


class AuroraDiagnostic:
    def __init__(self):
        self.issues = []
        self.root = Path("C:/Users/negry/Aurora-x")

    def check_server_status(self):
        """Check if Aurora server is responding"""
        print("=" * 80)
        print("[AURORA DIAGNOSTIC] Checking Server Status")
        print("=" * 80)
        print()

        # Check if server is running
        try:
            response = requests.get(
                "http://localhost:5000/api/aurora/status", timeout=5)
            if response.status_code == 200:
                print("[✓] Server is responding on port 5000")
                status = response.json()
                print(f"[✓] Aurora Status: {json.dumps(status, indent=2)}")
            else:
                print(
                    f"[✗] Server returned status code: {response.status_code}")
                self.issues.append(
                    f"Server status code: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("[✗] Cannot connect to server on port 5000")
            self.issues.append("Server not reachable on port 5000")
        except Exception as e:
            print(f"[✗] Error checking server: {e}")
            self.issues.append(f"Server check error: {e}")
        print()

    def test_aurora_analyze(self):
        """Test Aurora's analyze endpoint"""
        print("=" * 80)
        print("[AURORA DIAGNOSTIC] Testing Aurora Analyze Endpoint")
        print("=" * 80)
        print()

        try:
            response = requests.post(
                "http://localhost:5000/api/aurora/analyze",
                json={"input": "Test message from diagnostic",
                      "context": "diagnostic test"},
                timeout=10
            )

            if response.status_code == 200:
                print("[✓] Analyze endpoint responding")
                result = response.json()
                print(f"[✓] Response: {json.dumps(result, indent=2)}")
            else:
                print(f"[✗] Analyze endpoint returned: {response.status_code}")
                print(f"[✗] Error: {response.text}")
                self.issues.append(
                    f"Analyze endpoint error: {response.status_code}")
        except Exception as e:
            print(f"[✗] Cannot test analyze endpoint: {e}")
            self.issues.append(f"Analyze test failed: {e}")
        print()

    def check_python_bridge(self):
        """Check if Python bridge is working"""
        print("=" * 80)
        print("[AURORA DIAGNOSTIC] Checking Python Bridge")
        print("=" * 80)
        print()

        # Test if aurora_core.py can be imported
        try:
            result = subprocess.run(
                ["python", "-c",
                    "from aurora_core import AuroraCoreIntelligence; print('Python bridge OK')"],
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                print("[✓] Python aurora_core.py is importable")
                print(f"[✓] Output: {result.stdout.strip()}")
            else:
                print(f"[✗] Python import failed")
                print(f"[✗] Error: {result.stderr}")
                self.issues.append("Python bridge import failed")
        except Exception as e:
            print(f"[✗] Cannot test Python bridge: {e}")
            self.issues.append(f"Python bridge test failed: {e}")
        print()

    def check_websocket(self):
        """Check WebSocket server"""
        print("=" * 80)
        print("[AURORA DIAGNOSTIC] Checking WebSocket Server")
        print("=" * 80)
        print()

        # Check if WebSocket endpoint exists
        try:
            # WebSocket can't be tested with regular HTTP, but we can check if server acknowledges it
            response = requests.get("http://localhost:5000/", timeout=5)
            if response.status_code in [200, 404]:
                print(
                    "[✓] Server is accessible (WebSocket endpoint should be at ws://localhost:5000/aurora/chat)")
            else:
                print(
                    f"[?] Unexpected server response: {response.status_code}")
        except Exception as e:
            print(f"[✗] Cannot check WebSocket: {e}")
            self.issues.append(f"WebSocket check failed: {e}")
        print()

    def check_frontend(self):
        """Check if frontend is loading"""
        print("=" * 80)
        print("[AURORA DIAGNOSTIC] Checking Frontend")
        print("=" * 80)
        print()

        try:
            response = requests.get("http://localhost:5000/", timeout=5)
            if response.status_code == 200:
                print("[✓] Frontend is loading from server")
                if "<!DOCTYPE html>" in response.text or "<html" in response.text:
                    print("[✓] HTML content detected")
                else:
                    print("[?] Response doesn't look like HTML")
                    print(f"[?] First 200 chars: {response.text[:200]}")
            else:
                print(f"[✗] Frontend returned: {response.status_code}")
                self.issues.append(f"Frontend status: {response.status_code}")
        except Exception as e:
            print(f"[✗] Cannot check frontend: {e}")
            self.issues.append(f"Frontend check failed: {e}")
        print()

    def check_chat_endpoint(self):
        """Test the chat endpoint specifically"""
        print("=" * 80)
        print("[AURORA DIAGNOSTIC] Testing Chat Endpoint")
        print("=" * 80)
        print()

        try:
            # Try the Aurora chat endpoint
            response = requests.post(
                "http://localhost:5000/api/aurora/chat",
                json={"message": "Hello Aurora, can you hear me?"},
                timeout=15
            )

            if response.status_code == 200:
                print("[✓] Chat endpoint responding")
                result = response.json()
                print(f"[✓] Response: {json.dumps(result, indent=2)}")
            else:
                print(f"[✗] Chat endpoint returned: {response.status_code}")
                print(f"[✗] Response: {response.text[:500]}")
                self.issues.append(
                    f"Chat endpoint error: {response.status_code}")
        except requests.exceptions.Timeout:
            print("[✗] Chat endpoint timed out (took more than 15 seconds)")
            self.issues.append("Chat endpoint timeout")
        except Exception as e:
            print(f"[✗] Cannot test chat endpoint: {e}")
            self.issues.append(f"Chat test failed: {e}")
        print()

    def check_terminal_output(self):
        """Check what the server terminal is showing"""
        print("=" * 80)
        print("[AURORA DIAGNOSTIC] Server Terminal Status")
        print("=" * 80)
        print()
        print("[INFO] The server terminal should show:")
        print("  • '[AURORA] Initializing 188 power units...'")
        print("  • '[AURORA] ✅ Aurora initialized with 188 power units'")
        print("  • '[AURORA] ✅ Python bridge connected'")
        print("  • 'serving on port 5000'")
        print()
        print("[INFO] When you send a message, you should see:")
        print("  • Request logs in the terminal")
        print("  • Any errors or warnings")
        print()
        print(
            "[QUESTION] Do you see any errors in the terminal when you send a message?")
        print()

    def generate_report(self):
        """Generate diagnostic report"""
        print("=" * 80)
        print("[AURORA DIAGNOSTIC REPORT]")
        print("=" * 80)
        print()

        if not self.issues:
            print("✓ No critical issues detected")
            print()
            print("POSSIBLE CAUSES OF 'NO RESPONSE':")
            print("1. Frontend JavaScript error (check browser console F12)")
            print("2. Chat endpoint not properly connected to Aurora Core")
            print("3. Python bridge response not being returned properly")
            print("4. WebSocket connection not established")
            print("5. Response is being sent but frontend not displaying it")
        else:
            print(f"✗ Found {len(self.issues)} issues:")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")

        print()
        print("=" * 80)
        print("[NEXT STEPS]")
        print("=" * 80)
        print()
        print("1. Open browser console (F12) and check for JavaScript errors")
        print("2. Try sending a message and watch the terminal for errors")
        print("3. Check Network tab (F12) to see if requests are being sent")
        print("4. Look at server terminal for any error messages")
        print()
        print("Tell me what you see and Aurora will fix it!")
        print()

    def run_full_diagnostic(self):
        """Run complete diagnostic"""
        print()
        print("🔍" * 40)
        print()
        print("   AURORA DEEP DIAGNOSTIC")
        print("   Finding out why Aurora isn't responding")
        print()
        print("🔍" * 40)
        print()

        time.sleep(1)

        self.check_server_status()
        time.sleep(1)

        self.check_frontend()
        time.sleep(1)

        self.test_aurora_analyze()
        time.sleep(1)

        self.check_chat_endpoint()
        time.sleep(1)

        self.check_python_bridge()
        time.sleep(1)

        self.check_websocket()
        time.sleep(1)

        self.check_terminal_output()

        self.generate_report()


if __name__ == "__main__":
    diagnostic = AuroraDiagnostic()
    diagnostic.run_full_diagnostic()
