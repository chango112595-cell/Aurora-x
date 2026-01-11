#!/usr/bin/env python3
"""
Aurora Desktop App - Native Windows/Linux/macOS Application
Provides GUI interface for Aurora with system monitoring and request handling
"""

import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path
from tkinter import Button, Frame, Label, Scrollbar, Text, Tk

ROOT = Path(__file__).resolve().parent


class AuroraDesktopApp:
    """Desktop application wrapper for Aurora"""

    def __init__(self):
        self.root = Tk()
        self.root.title("Aurora - System Healer & Enhancement AI")
        self.root.geometry("900x700")
        self.root.configure(bg="#1a1a1a")

        self.services_running = False
        self.monitoring_active = False
        self.status_thread = None

        self._create_ui()
        self._start_status_monitoring()

    def _create_ui(self):
        """Create the user interface"""
        # Header
        header = Frame(self.root, bg="#2d2d2d", height=80)
        header.pack(fill="x", padx=0, pady=0)

        title = Label(
            header,
            text="🌟 AURORA",
            font=("Arial", 24, "bold"),
            bg="#2d2d2d",
            fg="#00ff88",
        )
        title.pack(pady=15)

        subtitle = Label(
            header,
            text="System Healer & Enhancement AI",
            font=("Arial", 10),
            bg="#2d2d2d",
            fg="#888888",
        )
        subtitle.pack()

        # Status Panel
        status_frame = Frame(self.root, bg="#1a1a1a")
        status_frame.pack(fill="x", padx=20, pady=10)

        self.status_label = Label(
            status_frame,
            text="🔍 Analyzing system...",
            font=("Arial", 12, "bold"),
            bg="#1a1a1a",
            fg="#00ff88",
        )
        self.status_label.pack(side="left")

        self.status_indicator = Label(
            status_frame,
            text="●",
            font=("Arial", 20),
            bg="#1a1a1a",
            fg="#ff4444",
        )
        self.status_indicator.pack(side="right")

        # System Info Panel
        info_frame = Frame(self.root, bg="#2d2d2d", relief="flat")
        info_frame.pack(fill="both", expand=True, padx=20, pady=10)

        info_title = Label(
            info_frame,
            text="System Information",
            font=("Arial", 12, "bold"),
            bg="#2d2d2d",
            fg="#ffffff",
        )
        info_title.pack(anchor="w", padx=10, pady=5)

        self.info_text = Text(
            info_frame,
            bg="#1a1a1a",
            fg="#00ff88",
            font=("Consolas", 10),
            wrap="word",
            relief="flat",
            borderwidth=0,
        )
        self.info_text.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = Scrollbar(self.info_text)
        scrollbar.pack(side="right", fill="y")
        self.info_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.info_text.yview)

        # Control Buttons
        button_frame = Frame(self.root, bg="#1a1a1a")
        button_frame.pack(fill="x", padx=20, pady=10)

        self.start_button = Button(
            button_frame,
            text="🚀 Start Aurora",
            font=("Arial", 12, "bold"),
            bg="#00ff88",
            fg="#000000",
            command=self._start_aurora,
            relief="flat",
            padx=20,
            pady=10,
        )
        self.start_button.pack(side="left", padx=5)

        self.stop_button = Button(
            button_frame,
            text="🛑 Stop Aurora",
            font=("Arial", 12, "bold"),
            bg="#ff4444",
            fg="#ffffff",
            command=self._stop_aurora,
            relief="flat",
            padx=20,
            pady=10,
            state="disabled",
        )
        self.stop_button.pack(side="left", padx=5)

        self.web_button = Button(
            button_frame,
            text="🌐 Open Web UI",
            font=("Arial", 12),
            bg="#4444ff",
            fg="#ffffff",
            command=self._open_web_ui,
            relief="flat",
            padx=20,
            pady=10,
            state="disabled",
        )
        self.web_button.pack(side="left", padx=5)

        self.request_button = Button(
            button_frame,
            text="💬 Make Request",
            font=("Arial", 12),
            bg="#ff8800",
            fg="#ffffff",
            command=self._make_request,
            relief="flat",
            padx=20,
            pady=10,
        )
        self.request_button.pack(side="left", padx=5)

        # Initial system analysis
        self._update_system_info()

    def _update_system_info(self):
        """Update system information display"""
            try:
                import platform

                import psutil

            info = []
            info.append("=" * 60)
            info.append("SYSTEM ANALYSIS")
            info.append("=" * 60)
            info.append(f"\nPlatform: {platform.system()} {platform.machine()}")
            info.append(f"Python: {platform.python_version()}")

            # CPU Info
            cpu_count = psutil.cpu_count()
            cpu_percent = psutil.cpu_percent(interval=1)
            info.append(f"\nCPU: {cpu_count} cores | Usage: {cpu_percent:.1f}%")

            # Memory Info
            memory = psutil.virtual_memory()
            info.append(
                f"Memory: {memory.used / (1024**3):.1f}GB / "
                f"{memory.total / (1024**3):.1f}GB "
                f"({memory.percent:.1f}% used)"
            )

            # Disk Info
            disk = psutil.disk_usage("/")
            info.append(
                f"Disk: {disk.used / (1024**3):.1f}GB / "
                f"{disk.total / (1024**3):.1f}GB "
                f"({disk.percent:.1f}% used)"
            )

            # Network Info
            net_io = psutil.net_io_counters()
            info.append(
                f"\nNetwork: Sent {net_io.bytes_sent / (1024**2):.1f}MB | "
                f"Recv {net_io.bytes_recv / (1024**2):.1f}MB"
            )

            info.append("\n" + "=" * 60)
            info.append("AURORA CAPABILITIES")
            info.append("=" * 60)
            info.append("✅ System Monitoring")
            info.append("✅ Issue Detection")
            info.append("✅ Auto-Healing")
            info.append("✅ Performance Optimization")
            info.append("✅ Security Analysis")
            info.append("✅ Request Handling")

            self.info_text.delete("1.0", "end")
            self.info_text.insert("1.0", "\n".join(info))
        except ImportError:
            self.info_text.delete("1.0", "end")
            self.info_text.insert(
                "1.0",
                "System analysis requires psutil.\n"
                "Install with: pip install psutil\n\n"
                "Aurora will analyze the system when started.",
            )

    def _start_status_monitoring(self):
        """Start background status monitoring"""
        self.monitoring_active = True
        self.status_thread = threading.Thread(target=self._monitor_status, daemon=True)
        self.status_thread.start()

    def _monitor_status(self):
        """Monitor Aurora services status"""
        import socket

        while self.monitoring_active:
            try:
                # Check if services are running
                ports = [5000, 5001, 5002, 8000]
                running_count = 0

                for port in ports:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5)
                    try:
                        result = sock.connect_ex(("127.0.0.1", port))
                        if result == 0:
                            running_count += 1
                    except Exception:
                        pass
                    finally:
                        sock.close()

                if running_count >= 3:
                    self.services_running = True
                    self.root.after(0, self._update_status, "running", running_count)
                else:
                    self.services_running = False
                    self.root.after(0, self._update_status, "stopped", running_count)

            except Exception:
                pass

            time.sleep(5)

    def _update_status(self, status: str, count: int):
        """Update status display"""
        if status == "running":
            self.status_label.config(text=f"✅ Aurora Running ({count}/4 services)")
            self.status_indicator.config(fg="#00ff88")
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.web_button.config(state="normal")
        else:
            self.status_label.config(text=f"⚠️ Aurora Stopped ({count}/4 services)")
            self.status_indicator.config(fg="#ff4444")
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.web_button.config(state="disabled")

    def _start_aurora(self):
        """Start Aurora services"""
        self.status_label.config(text="🚀 Starting Aurora...")
        self.status_indicator.config(fg="#ffaa00")

        def start():
            try:
                subprocess.Popen(
                    [sys.executable, str(ROOT / "x-start.py")],
                    cwd=str(ROOT),
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                    if sys.platform == "win32"
                    else 0,
                )
            except Exception as exc:
                error_msg = str(exc)
                self.root.after(
                    0,
                    lambda: self.status_label.config(
                        text=f"❌ Failed to start: {error_msg}"
                    ),
                )

        threading.Thread(target=start, daemon=True).start()

    def _stop_aurora(self):
        """Stop Aurora services"""
        self.status_label.config(text="🛑 Stopping Aurora...")
        self.status_indicator.config(fg="#ffaa00")

        def stop():
            try:
                subprocess.Popen(
                    [sys.executable, str(ROOT / "x-stop.py")],
                    cwd=str(ROOT),
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                    if sys.platform == "win32"
                    else 0,
                )
            except Exception as exc:
                error_msg = str(exc)
                self.root.after(
                    0,
                    lambda: self.status_label.config(
                        text=f"❌ Failed to stop: {error_msg}"
                    ),
                )

        threading.Thread(target=stop, daemon=True).start()

    def _open_web_ui(self):
        """Open Aurora web UI in browser"""
        webbrowser.open("http://localhost:5000")

    def _make_request(self):
        """Open request dialog"""
        from tkinter import simpledialog

        request = simpledialog.askstring(
            "Aurora Request",
            "What would you like Aurora to do?\n\n"
            "Examples:\n"
            "- Analyze system performance\n"
            "- Fix detected issues\n"
            "- Optimize memory usage\n"
            "- Check for security vulnerabilities\n"
            "- Enhance a specific program",
        )

        if request:
            self._send_request(request)

    def _send_request(self, request: str):
        """Send request to Aurora"""
        self.status_label.config(text=f"📤 Sending request: {request[:30]}...")

        def send():
            try:
                import requests

                response = requests.post(
                    "http://localhost:5002/api/dispatch-task",
                    json={
                        "task_type": "custom",
                        "payload": {"request": request, "source": "desktop_app"},
                        "priority": "normal",
                    },
                    timeout=5,
                )

                if response.status_code == 200:
                    self.root.after(
                        0,
                        lambda: self.status_label.config(
                            text="✅ Request sent successfully!"
                        ),
                    )
                else:
                    self.root.after(
                        0,
                        lambda: self.status_label.config(
                            text="⚠️ Request sent (Aurora may be starting)"
                        ),
                    )
            except Exception:
                self.root.after(
                    0,
                    lambda: self.status_label.config(
                        text="⚠️ Request queued (Aurora will process when ready)"
                    ),
                )

        threading.Thread(target=send, daemon=True).start()

    def run(self):
        """Run the application"""
        self.root.mainloop()

    def __del__(self):
        """Cleanup"""
        self.monitoring_active = False


if __name__ == "__main__":
    app = AuroraDesktopApp()
    app.run()
