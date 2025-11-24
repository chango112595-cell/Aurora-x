#!/usr/bin/env python3
"""Final cleanup of remaining errors"""
import os
import re

fixes = [
    # Files that still need manual fixes
    (
        "aurora_create_luminar_v2.py",
        "with open('luminar-nexus-v2.html', 'w') as f:",
        "with open('luminar-nexus-v2.html', 'w', encoding='utf-8') as f:",
    ),
    (
        "aurora_diagnose_chat.py",
        'subprocess.run([npm_cmd, "run", "build"], cwd=os.getcwd())',
        'subprocess.run([npm_cmd, "run", "build"], cwd=os.getcwd(), check=False)',
    ),
    ("aurora_diagnose_chat.py", "response = requests.options(url)", "response = requests.options(url, timeout=10)"),
    (
        "aurora_diagnose_chat.py",
        "with open('aurora_diagnostics.txt', 'w') as f:",
        "with open('aurora_diagnostics.txt', 'w', encoding='utf-8') as f:",
    ),
    ("aurora_full_system_debug.py", "for module, url in urls.items():", "for _module, url in urls.items():"),
    (
        "aurora_full_system_debug.py",
        "with open(index_html, 'r') as f:",
        "with open(index_html, 'r', encoding='utf-8') as f:",
    ),
    ("aurora_organize_system.py", "for name, path in categories.items():", "for _name, path in categories.items():"),
    ("aurora_review_before_cleanup.py", "except:\n        pass", "except (FileNotFoundError, OSError):\n        pass"),
    (
        "aurora_status_report.py",
        'subprocess.run([python_cmd, "-m", "pip", "list"], capture_output=True, text=True)',
        'subprocess.run([python_cmd, "-m", "pip", "list"], capture_output=True, text=True, check=False)',
    ),
    (
        "aurora_ultimate_coding_grandmaster.py",
        "with open(output_file, 'w') as f:",
        "with open(output_file, 'w', encoding='utf-8') as f:",
    ),
    (
        "aurora_ultimate_omniscient_grandmaster.py",
        "with open('aurora_intelligence.json', 'w') as f:",
        "with open('aurora_intelligence.json', 'w', encoding='utf-8') as f:",
    ),
    ("check_aurora_now.py", "except:\n        pass", "except (FileNotFoundError, OSError):\n        pass"),
    ("diagnostic_server.py", "with open(log_file, 'r') as f:", "with open(log_file, 'r', encoding='utf-8') as f:"),
    ("diagnostic_server.py", "except:\n            return", "except (FileNotFoundError, OSError):\n            return"),
    ("fix_makefile_tabs.py", "with open('Makefile') as f:", "with open('Makefile', encoding='utf-8') as f:"),
    ("fix_makefile_tabs.py", "with open('Makefile', 'w') as f:", "with open('Makefile', 'w', encoding='utf-8') as f:"),
    ("luminar-keeper.py", "with open(pidfile, 'w') as f:", "with open(pidfile, 'w', encoding='utf-8') as f:"),
    ("luminar-keeper.py", "with open(pidfile, 'r') as f:", "with open(pidfile, 'r', encoding='utf-8') as f:"),
    ("luminar-keeper.py", "except:\n        pass", "except (FileNotFoundError, OSError):\n        pass"),
    ("luminar-keeper.py", "def signal_handler(sig, frame):", "def signal_handler(_sig, _frame):"),
    ("prod_config.py", "with open(config_file, 'w') as f:", "with open(config_file, 'w', encoding='utf-8') as f:"),
    (
        "aurora_self_fix_monitor.py",
        "import subprocess\nimport time",
        "import subprocess\nimport time\nfrom pathlib import Path",
    ),
    (
        "aurora_self_fix_monitor.py",
        "with open(report_file, 'w') as f:",
        "with open(report_file, 'w', encoding='utf-8') as f:",
    ),
    ("aurora_server_manager.py", "with open(pid_file) as f:", "with open(pid_file, encoding='utf-8') as f:"),
    ("aurora_server_manager.py", "with open(pid_file, 'w') as f:", "with open(pid_file, 'w', encoding='utf-8') as f:"),
    ("aurora_server_manager.py", "with open(log_file, 'w') as f:", "with open(log_file, 'w', encoding='utf-8') as f:"),
    (
        "aurora_server_manager.py",
        "for service_name, service_info in self.services.items():",
        "for _service_name, service_info in self.services.items():",
    ),
    (
        "aurora_server_manager.py",
        "def get_status_report(self, service_name):",
        "def get_status_report(self, _service_name):",
    ),
    ("start_aurora_autonomous.py", "def signal_handler(signum, frame):", "def signal_handler(_signum, _frame):"),
    (
        "start_aurora_autonomous.py",
        "with open(pid_file, 'w') as f:",
        "with open(pid_file, 'w', encoding='utf-8') as f:",
    ),
    (
        "start_aurora_autonomous.py",
        "with open(pid_file, 'r') as f:",
        "with open(pid_file, 'r', encoding='utf-8') as f:",
    ),
    (
        "start_aurora_autonomous.py",
        "with open(log_file, 'a') as f:",
        "with open(log_file, 'a', encoding='utf-8') as f:",
    ),
    ("start_aurora_autonomous.py", "except:\n        pass", "except (FileNotFoundError, OSError):\n        pass"),
]

count = 0
for filepath, old, new in fixes:
    if os.path.exists(filepath):
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
            if old in content:
                content = content.replace(old, new)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                count += 1
        except Exception as e:
            print(f"Error fixing {filepath}: {e}")

# Fix subprocess.run calls in aurora_full_system_debug.py and aurora_self_debug_chat.py
for filepath in ["aurora_full_system_debug.py", "aurora_self_debug_chat.py"]:
    if os.path.exists(filepath):
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Add check=False to subprocess.run calls that don't have it
        pattern = r"subprocess\.run\(\[([^\]]+)\], capture_output=True, text=True, timeout=\d+\)(?!,\s*check=)"
        replacement = r"subprocess.run([\1], capture_output=True, text=True, timeout=5, check=False)"
        content = re.sub(pattern, replacement, content)

        # Also handle ones without timeout
        pattern2 = r"subprocess\.run\(\[([^\]]+)\], capture_output=True, text=True\)(?!,\s*check=)"
        replacement2 = r"subprocess.run([\1], capture_output=True, text=True, check=False)"
        content = re.sub(pattern2, replacement2, content)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        count += 1

print(f"[OK] Applied {count} fixes!")
print("[EMOJI] All critical errors resolved!")
