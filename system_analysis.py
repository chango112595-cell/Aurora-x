"""
AURORA COMPLETE SYSTEM ANALYSIS
Comprehensive diagnostic of all Aurora components
"""
import os
import json
import sys

print("\n" + "="*60)
print("AURORA COMPLETE SYSTEM ANALYSIS")
print("="*60 + "\n")

# 1. CRITICAL FILES CHECK
print("1. CRITICAL FILES STATUS:")
critical_files = {
    "aurora_core.py": "Python intelligence core",
    "server/aurora-chat.ts": "TypeScript chat bridge",
    "app/api/chat/route.ts": "Next.js API endpoint",
    "client/src/components/AuroraFuturisticChat.tsx": "React chat UI"
}

for file, desc in critical_files.items():
    exists = "✓ EXISTS" if os.path.exists(file) else "✗ MISSING"
    print(f"   {exists} - {file} ({desc})")

# 2. SESSION DATA
print("\n2. SESSION/MEMORY STATUS:")
sessions_dir = ".aurora/sessions"
if os.path.exists(sessions_dir):
    sessions = [f for f in os.listdir(sessions_dir) if f.endswith('.json')]
    print(f"   Total sessions: {len(sessions)}")
    if sessions:
        print(f"   Latest: {sessions[-1]}")
        # Check if sessions have data
        latest_path = os.path.join(sessions_dir, sessions[-1])
        try:
            with open(latest_path, 'r') as f:
                data = json.load(f)
                print(
                    f"   Memory working: {'user_name' in data or 'message_count' in data}")
        except:
            print("   Memory working: Unknown (could not read)")
else:
    print("   ✗ Sessions directory missing")

# 3. PYTHON CORE STATUS
print("\n3. PYTHON CORE STATUS:")
try:
    sys.path.insert(0, '.')
    from aurora_core import AuroraCoreIntelligence
    aurora = AuroraCoreIntelligence()
    print(f"   ✓ Import successful")
    print(f"   Total Power Units: {aurora.total_power}")
    print(f"   Knowledge: {aurora.knowledge_units}")
    print(f"   Execution: {aurora.execution_units}")
    print(f"   Systems: {aurora.system_units}")
except Exception as e:
    print(f"   ✗ Error: {str(e)[:100]}")

# 4. TYPESCRIPT FILES STATUS
print("\n4. TYPESCRIPT BUILD STATUS:")
ts_files = [
    "server/aurora-chat.ts",
    "app/api/chat/route.ts",
    "client/src/components/AuroraFuturisticChat.tsx"
]
for ts_file in ts_files:
    if os.path.exists(ts_file):
        size = os.path.getsize(ts_file)
        print(f"   ✓ {ts_file} ({size} bytes)")
    else:
        print(f"   ✗ {ts_file} MISSING")

# 5. CONFIGURATION FILES
print("\n5. CONFIGURATION FILES:")
config_files = ["package.json", "tsconfig.json", "next.config.js"]
for config in config_files:
    exists = "✓" if os.path.exists(config) else "✗"
    print(f"   {exists} {config}")

# 6. BUILD STATUS
print("\n6. BUILD ARTIFACTS:")
artifacts = [".next", "node_modules", ".aurora"]
for artifact in artifacts:
    exists = "✓" if os.path.exists(artifact) else "✗"
    print(f"   {exists} {artifact}")

print("\n" + "="*60)
print("ANALYSIS COMPLETE")
print("="*60 + "\n")
