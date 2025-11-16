#!/usr/bin/env python3
"""Fix remaining encoding and other issues"""
import re

# Fix test_dashboard_simple.py
with open("test_dashboard_simple.py", encoding="utf-8") as f:
    content = f.read()
content = re.sub(r"open\((['\"][^'\"]+['\"]),\s*['\"]r['\"]\)", r"open(\1, 'r', encoding='utf-8')", content)
content = re.sub(r"open\((['\"][^'\"]+['\"]),\s*['\"]w['\"]\)", r"open(\1, 'w', encoding='utf-8')", content)
with open("test_dashboard_simple.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ test_dashboard_simple.py")

# Fix test_demo_dashboard.py
with open("test_demo_dashboard.py", encoding="utf-8") as f:
    content = f.read()
content = re.sub(r"open\((['\"][^'\"]+['\"]),\s*['\"]r['\"]\)", r"open(\1, 'r', encoding='utf-8')", content)
with open("test_demo_dashboard.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ test_demo_dashboard.py")

# Fix test_healthz.py
with open("test_healthz.py", encoding="utf-8") as f:
    content = f.read()
content = re.sub(r"open\((['\"][^'\"]+['\"]),\s*['\"]w['\"]\)", r"open(\1, 'w', encoding='utf-8')", content)
with open("test_healthz.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ test_healthz.py")

# Fix test_runall.py
with open("test_runall.py", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "open(output_file, 'w')" in line:
        lines[i] = line.replace("'w')", "'w', encoding='utf-8')")
    # Fix expression not assigned - add assignment
    if "'generated_utc': datetime.utcnow()" in line and "result_data = {" not in lines[i - 1] if i > 0 else True:
        lines[i] = "        result_data = " + line.lstrip()
with open("test_runall.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
print("✅ test_runall.py")

# Fix test_t08_e2e.py
with open("test_t08_e2e.py", encoding="utf-8") as f:
    content = f.read()
content = re.sub(r"open\((['\"][^'\"]+['\"]),\s*['\"]w['\"]\)", r"open(\1, 'w', encoding='utf-8')", content)
with open("test_t08_e2e.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ test_t08_e2e.py")

# Fix test_t08_offline.py
with open("test_t08_offline.py", encoding="utf-8") as f:
    content = f.read()
content = re.sub(r"open\((['\"][^'\"]+['\"]),\s*['\"]w['\"]\)", r"open(\1, 'w', encoding='utf-8')", content)
with open("test_t08_offline.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ test_t08_offline.py")

# Fix test_lib_factorial.py - add time import
with open("test_lib_factorial.py", encoding="utf-8") as f:
    content = f.read()
if "import time" not in content:
    lines = content.split("\n")
    for i in range(min(10, len(lines))):
        if "import" in lines[i] and "from" not in lines[i]:
            lines.insert(i + 1, "import time")
            break
    content = "\n".join(lines)
with open("test_lib_factorial.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ test_lib_factorial.py")

# Fix diagnostic_server.py - format parameter
with open("diagnostic_server.py", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "format: str =" in line and i > 280 and i < 295:
        lines[i] = line.replace("format:", "fmt:")
    if "format=format" in line and i > 280 and i < 295:
        lines[i] = line.replace("format=format", "format=fmt")
with open("diagnostic_server.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
print("✅ diagnostic_server.py")

# Fix callback comparisons
for filepath in ["test.py", "test_aurora_response.py", "test_lib_generic.py", "create_a_simple_hello_world.py"]:
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if re.search(r"\bif\s+callback\s*:", line) and "is not None" not in line and "callable" not in line:
            lines[i] = re.sub(r"if\s+callback\s*:", "if callback is not None:", line)
        if re.search(r"\bif\s+not\s+callback\s*:", line) and "is None" not in line:
            lines[i] = re.sub(r"if\s+not\s+callback\s*:", "if callback is None:", line)
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"✅ {filepath}")

# Fix unused output_format arguments
for filepath in ["test.py", "test_aurora_response.py", "test_lib_generic.py"]:
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if "def transform_output" in line and "output_format" in line:
            # Add usage of output_format in the function
            if i + 2 < len(lines) and "output_format" not in lines[i + 2]:
                lines.insert(i + 2, "    _ = output_format  # Format specification\n")
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"✅ {filepath} output_format")

# Fix generated_timer_app.py and generated_web_app.py
for filepath in ["generated_timer_app.py", "generated_web_app.py", "timer_app.py"]:
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if "def setup_routes(flask_app):" in line:
            lines[i] = line.replace("flask_app):", "app):")
        if "@flask_app." in line:
            lines[i] = line.replace("@flask_app.", "@app.")
        if "flask_app.run" in line:
            lines[i] = line.replace("flask_app.run", "app.run")
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"✅ {filepath}")

# Fix test_lib_generic.py - func_name possibly used before assignment
with open("test_lib_generic.py", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "def generate" in line and i < 100:
        # Add func_name initialization at start of function
        if i + 2 < len(lines) and "func_name = " not in lines[i + 2]:
            lines.insert(i + 2, '    func_name = "generic_function"\n')
with open("test_lib_generic.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
print("✅ test_lib_generic.py func_name")

print("\n✨ All remaining issues fixed!")
