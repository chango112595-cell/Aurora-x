#!/usr/bin/env python3
"""
Secure CLI to set secrets in the ASE-∞ vault
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ase_vault import set_secret_cli

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: vault_set.py <alias> <master_passphrase> [layers]")
        sys.exit(2)
    
    alias = sys.argv[1]
    master = sys.argv[2]
    layers = int(sys.argv[3]) if len(sys.argv) >= 4 else None
    
    val = input("Enter secret value (paste, then Enter): ").strip()
    
    if layers:
        ok = set_secret_cli(alias, val, master, layers=layers)
    else:
        ok = set_secret_cli(alias, val, master)
    
    if ok:
        print("Saved:", alias)
