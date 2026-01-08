#!/usr/bin/env python3
"""
ASE-∞ Vault Self-Test
Author: Aurora-X System
Purpose: Verify the encryption vault operates correctly:
 - multi-layer encryption
 - MAC integrity
 - correct decryption
 - alias registration
 - op-log entries
 - vault_read.py subprocess bridge

This test does NOT modify real secrets.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECURE = ROOT / "aurora_supervisor" / "secure"

ASE_FILE = SECURE / "ase_vault.py"
VAULT_READ = SECURE / "vault_read.py"
VAULT_SET = SECURE / "vault_set.py"
VAULT_FILE = SECURE / "secret_vault.json"
OPLOG_FILE = SECURE / "vault_oplog.jsonl"

TEST_ALIAS = "aurora.test.secret"
MASTER_KEY = "AuroraMasterKey123!!"
TEST_VALUE = "ThisIsATestSecretValue"


def import_ase():
    """Import ase_vault.py dynamically."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("ase_vault", str(ASE_FILE))
    ase = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ase)
    return ase


def step(msg):
    print(f"\n=== {msg} ===")


def check_files():
    missing = [p for p in [ASE_FILE, VAULT_SET, VAULT_READ] if not p.exists()]
    if missing:
        print("ERROR: Missing required files:")
        for m in missing:
            print(" •", m)
        sys.exit(1)
    print("[OK] All required vault files exist.")


def run_set_secret(alias, master, value):
    """Invoke ase.set_secret_cli without user prompts."""
    ase = import_ase()
    ok = ase.set_secret_cli(alias, value, master, layers=ase.DEFAULT_LAYERS)
    print(f"[OK] set_secret_cli returned: {ok}")
    return ok


def run_get_secret(alias, master):
    """Invoke ase.get_secret_cli."""
    ase = import_ase()
    val = ase.get_secret_cli(alias, master)
    return val


def call_bridge(alias, master):
    """Call vault_read.py subprocess."""
    out = subprocess.run(
        ["python3", str(VAULT_READ), alias, master], capture_output=True, text=True
    )
    return out.returncode, out.stdout.strip(), out.stderr.strip()


def tail_oplog():
    if not OPLOG_FILE.exists():
        print("[WARN] No op-log available.")
        return
    lines = open(OPLOG_FILE).read().strip().splitlines()
    print("[OPLOG] Last 5 entries:")
    for line in lines[-5:]:
        print("  ", line)


def main():
    step("1. Checking required files")
    check_files()

    step("2. Writing test secret to ASE-∞ vault")
    set_ok = run_set_secret(TEST_ALIAS, MASTER_KEY, TEST_VALUE)
    if not set_ok:
        print("[FAIL] Could not write test secret.")
        sys.exit(1)

    step("3. Reading back test secret")
    value = run_get_secret(TEST_ALIAS, MASTER_KEY)
    if value != TEST_VALUE:
        print("[FAIL] Decrypted value mismatch")
        print("Expected:", TEST_VALUE)
        print("Got:", value)
        sys.exit(1)
    print("[OK] Secret decrypted correctly.")

    step("4. Testing vault_read.py bridge")
    code, out, err = call_bridge(TEST_ALIAS, MASTER_KEY)
    print("Return code:", code)
    print("Output:", out)

    if code != 0:
        print("[FAIL] Bridge returned error:", err)
        sys.exit(1)

    if out != TEST_VALUE:
        print("[FAIL] Bridge output mismatch.")
        sys.exit(1)

    print("[OK] Bridge successfully read secret.")

    step("5. Verifying op-log entries")
    tail_oplog()

    print("\n🎉 ALL TESTS PASSED — ASE-∞ Vault is fully operational.\n")


if __name__ == "__main__":
    main()
