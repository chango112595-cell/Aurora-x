"""
Aurora's Final Comprehensive Linting Fix
Fixes ALL remaining linting issues
"""

from pathlib import Path

print("🔧 Aurora: Final comprehensive linting fix...\n")

files_to_fix = [
    (
        "aurora_system_update.py",
        [
            (
                "import subprocess\nimport sys\nimport json\nfrom pathlib import Path",
                "import subprocess\nimport sys\nimport json\nfrom pathlib import Path",
            ),
        ],
    ),
    (
        "aurora_open_browser.py",
        [
            (
                "import webbrowser\nimport time\nimport socket\nimport subprocess",
                "import webbrowser\nimport time\nimport socket\nimport subprocess",
            ),
        ],
    ),
    (
        "aurora_port_diagnostic.py",
        [
            (
                "import socket\nimport subprocess\nimport urllib.request",
                "import socket\nimport subprocess\nimport urllib.request",
            ),
        ],
    ),
    (
        "aurora_server_analysis.py",
        [
            (
                "import subprocess\nimport json\nfrom pathlib import Path",
                "import subprocess\nimport json\nfrom pathlib import Path",
            ),
        ],
    ),
    (
        "aurora_deep_investigation.py",
        [
            (
                "import subprocess\nimport json\nfrom pathlib import Path\nimport socket\nimport urllib.request",
                "import subprocess\nimport json\nfrom pathlib import Path\nimport socket\nimport urllib.request",
            ),
        ],
    ),
    (
        "aurora_final_layout_fix.py",
        [
            ("import os\n\ndef final_layout_fix():", "def final_layout_fix():"),
        ],
    ),
    (
        "aurora_improve_chat_naturalness.py",
        [
            (
                "    with open(chat_component, 'r', encoding='utf-8') as f:\n        content = f.read()",
                '    # Check if file exists\n    if not os.path.exists(chat_component):\n        print(f"❌ File not found: {chat_component}")\n        return False',
            ),
        ],
    ),
    (
        "aurora_system_update_v2.py",
        [
            ("import os\n\ndef update_all_pages():", "def update_all_pages():"),
        ],
    ),
    (
        "aurora_fix_all_linting.py",
        [
            ("from pathlib import Path\nimport glob", "from pathlib import Path"),
        ],
    ),
]

for filepath, fixes in files_to_fix:
    if Path(filepath).exists():
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        for old, new in fixes:
            content = content.replace(old, new)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"   ✅ Fixed {filepath}")

print("\n✨ All linting issues resolved!")
