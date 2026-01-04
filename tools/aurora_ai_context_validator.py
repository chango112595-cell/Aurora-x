#!/usr/bin/env python3
"""
Aurora AI Context Validator - Portable Repository State Inspector

This script validates the complete Aurora project structure and can export
a JSON snapshot for transferring project knowledge to new AI chat sessions.

Usage:
  python3 tools/aurora_ai_context_validator.py --run-tests --compute-zip-sha --check-docker
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def validate_packs():
    """Validate all 24 packs exist with proper structure."""
    packs_dir = Path("packs")
    expected_packs = [
        "pack01_pack01",
        "pack02_env_profiler",
        "pack03_os_base",
        "pack04_launcher",
        "pack05_5E_capability_system",
        "pack05_5F_event_hooks",
        "pack05_5G_permissions_resolver",
        "pack05_5H_plugin_store",
        "pack05_5I_versioning_upgrades",
        "pack05_5J_state_persistence",
        "pack05_5K_diagnostics",
        "pack05_5L_test_framework",
        "pack05_plugin_api",
        "pack05_plugin_loader",
        "pack06_firmware_system",
        "pack07_secure_signing",
        "pack08_conversational_engine",
        "pack09_compute_layer",
        "pack10_autonomy_engine",
        "pack11_device_mesh",
        "pack12_toolforge",
        "pack13_runtime_2",
        "pack14_hw_abstraction",
        "pack15_intel_fabric",
    ]
    
    packs_found = []
    packs_missing = []
    
    for pack in expected_packs:
        pack_path = packs_dir / pack
        if pack_path.exists() and (pack_path / "manifest.yaml").exists():
            packs_found.append(pack)
        else:
            packs_missing.append(pack)
    
    return {
        "total": len(expected_packs),
        "found": len(packs_found),
        "missing": len(packs_missing),
        "packs_found": packs_found,
        "packs_missing": packs_missing,
    }

def validate_infrastructure():
    """Validate supporting infrastructure."""
    infrastructure = {
        "deploy": Path("deploy").exists(),
        "docker": Path("docker").exists(),
        "docs": Path("docs").exists(),
        "tools": Path("tools").exists(),
        "monitoring": Path("monitoring").exists(),
        "ops": Path("ops").exists(),
        "sign_tools": Path("sign_tools").exists(),
        "aurora_webui": Path("aurora_webui").exists(),
        "installer": Path("installer").exists(),
    }
    return infrastructure

def run_tests():
    """Run pack tests."""
    try:
        result = subprocess.run(
            ["python3", "run_pack_tests.py"],
            capture_output=True,
            timeout=300,
            text=True
        )
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "output_lines": len(result.stdout.split("\n")),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def compute_checksums():
    """Compute checksums for bundles."""
    checksums = {}
    for bundle in ["packs_full_bundle.zip", "aurora_os_bundle.zip"]:
        path = Path(bundle)
        if path.exists():
            try:
                result = subprocess.run(
                    ["sha256sum", str(path)],
                    capture_output=True,
                    text=True
                )
                checksums[bundle] = result.stdout.split()[0] if result.stdout else "error"
            except:
                checksums[bundle] = "error"
        else:
            checksums[bundle] = "not_found"
    return checksums

def check_docker():
    """Check Docker daemon availability."""
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            timeout=5,
            text=True
        )
        return {"available": result.returncode == 0}
    except:
        return {"available": False, "note": "Docker daemon not available (safe in development)"}

def generate_summary(args):
    """Generate complete project summary."""
    summary = {
        "timestamp": datetime.now().isoformat(),
        "project": "Aurora",
        "version": "1.0-final",
        "packs": validate_packs(),
        "infrastructure": validate_infrastructure(),
    }
    
    if "--run-tests" in args:
        print("[*] Running pack tests...")
        summary["tests"] = run_tests()
    
    if "--compute-zip-sha" in args:
        print("[*] Computing checksums...")
        summary["checksums"] = compute_checksums()
    
    if "--check-docker" in args:
        print("[*] Checking Docker...")
        summary["docker"] = check_docker()
    
    return summary

def main():
    """Main entry point."""
    args = sys.argv[1:]
    
    print("=== Aurora AI Context Validator ===\n")
    
    # Generate summary
    summary = generate_summary(args)
    
    # Print results
    print(f"✅ Total Packs: {summary['packs']['found']}/{summary['packs']['total']}")
    print(f"✅ Infrastructure: {sum(summary['infrastructure'].values())}/9 components")
    
    if "tests" in summary:
        status = "✅ PASS" if summary["tests"]["success"] else "❌ FAIL"
        print(f"{status} Tests")
    
    if "docker" in summary:
        status = "✅ Available" if summary["docker"]["available"] else "⚠️ Unavailable (dev mode ok)"
        print(f"{status} Docker")
    
    # Save summary to JSON
    summary_file = Path("tools/aurora_ai_context_summary.json")
    summary_file.write_text(json.dumps(summary, indent=2))
    print(f"\n📄 Summary saved to: {summary_file}")
    
    # Print portable context message
    print("\n" + "="*60)
    print("🟦 PORTABLE CONTEXT MESSAGE (paste into new AI chat):")
    print("="*60)
    print(open("replit.md").read().split("## 🔥 9. CONTEXT TRANSFER MESSAGE")[1].split("---")[0])
    
    return 0 if summary["packs"]["missing"] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())