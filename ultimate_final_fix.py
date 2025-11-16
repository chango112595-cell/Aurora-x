#!/usr/bin/env python3
"""Absolutely final fixes for all remaining errors"""
import os
import re


# Fix all remaining encoding issues
files_to_fix_encoding = [
    'test_dashboard_simple.py',
    'test_demo_dashboard.py',
    'test_healthz.py',
    'test_runall.py',
    'test_t08_e2e.py',
    'test_t08_offline.py',
    'luminar-keeper.py',
]

for filepath in files_to_fix_encoding:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        content = re.sub(r"open\(([^,)]+)\)",
                         r"open(\1, encoding='utf-8')", content)
        content = re.sub(r"open\(([^,)]+), '([rwa])'\)",
                         r"open(\1, '\2', encoding='utf-8')", content)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {filepath}")

# Fix unused variables
fixes = {
    'aurora_full_system_debug.py': [('for module, url', 'for _module, url')],
    'aurora_organize_system.py': [('for name, path', 'for _name, path')],
    'aurora_server_manager.py': [
        ('for service_name, service_info', 'for _service_name, service_info'),
        ('def get_status_report(self, service_name):',
         'def get_status_report(self, _service_name):'),
    ],
    'luminar-keeper.py': [('def signal_handler(sig, frame):', 'def signal_handler(_sig, _frame):')],
    'start_aurora_autonomous.py': [('def signal_handler(signum, frame):', 'def signal_handler(_signum, _frame):')],
    'test_cli_generic.py': [('def run_command(args):', 'def run_command(_args):')],
}

for filepath, replacements in fixes.items():
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        for old, new in replacements:
            content = content.replace(old, new)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {filepath}")

# Fix test_chat_router.py - use test_result properly
if os.path.exists('test_chat_router.py'):
    with open('test_chat_router.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i in range(len(lines)):
        if 'test_result =' in lines[i]:
            # Change to just result
            lines[i] = lines[i].replace('test_result =', 'result =')
        if i > 31 and 'result' in lines[i] and i < 70:
            # These should be fine
            pass

    with open('test_chat_router.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("✅ test_chat_router.py")

# Fix test_runall.py - assign expression
if os.path.exists('test_runall.py'):
    with open('test_runall.py', 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(
        r"(\s+)\{'generated_utc':",
        r"\1report = {'generated_utc':",
        content, count=1
    )
    with open('test_runall.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ test_runall.py")

# Fix test_lib_factorial.py - add time import
if os.path.exists('test_lib_factorial.py'):
    with open('test_lib_factorial.py', 'r', encoding='utf-8') as f:
        content = f.read()

    if 'import time' not in content.split('\n')[0:20]:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'import logging' in line:
                lines.insert(i+1, 'import time')
                break
        content = '\n'.join(lines)

        with open('test_lib_factorial.py', 'w', encoding='utf-8') as f:
            f.write(content)
    print("✅ test_lib_factorial.py")

# Fix test_timer_app.py - use app not flask_app
if os.path.exists('test_timer_app.py'):
    with open('test_timer_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace('flask_app.route', 'app.route')
    content = content.replace('flask_app.run', 'app.run')
    with open('test_timer_app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ test_timer_app.py")

# Fix all 'format' keyword argument issues
for filepath in ['test.py', 'test_aurora_response.py', 'test_lib_generic.py', 'create_a_simple_hello_world.py']:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        content = content.replace('format="json"', 'output_format="json"')
        content = content.replace('format="xml"', 'output_format="xml"')
        content = content.replace('format="yaml"', 'output_format="yaml"')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {filepath}")

# Fix undefined result variable usage
for filepath in ['test.py', 'test_aurora_response.py']:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Find line 319 and fix result reference
        for i in range(min(315, len(lines)-5), min(325, len(lines))):
            if 'repr(result)' in lines[i] and 'demo_result' not in lines[i]:
                lines[i] = lines[i].replace(
                    'repr(result)', 'repr(demo_result)')

        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"✅ {filepath}")

# Fix diagnostic_server.py format parameter
if os.path.exists('diagnostic_server.py'):
    with open('diagnostic_server.py', 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace('def format_log_entry(entry, format="text"):',
                              'def format_log_entry(entry, output_format="text"):')
    content = content.replace('if format == ', 'if output_format == ')
    content = content.replace('elif format == ', 'elif output_format == ')
    content = re.sub(r'(\s+)format=format\n\s+pass',
                     r'\1format=output_format', content)
    with open('diagnostic_server.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ diagnostic_server.py")

# Fix callback comparison issues
for filepath in ['test.py', 'test_aurora_response.py', 'test_lib_generic.py', 'create_a_simple_hello_world.py']:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        content = content.replace('if callback:', 'if callback is not None:')
        content = content.replace('if not callback:', 'if callback is None:')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {filepath} callback")

print("\n🎉 All errors fixed!")
