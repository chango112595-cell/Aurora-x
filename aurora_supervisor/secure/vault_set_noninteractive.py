#!/usr/bin/env python3
"""
Non-interactive CLI to set secrets in the ASE-∞ vault
Used by the Node.js vault bridge for API-based secret storage
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ase_vault import set_secret_cli

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("usage: vault_set_noninteractive.py <alias> <master_passphrase> <value> [layers]")
        sys.exit(2)
    
    alias = sys.argv[1]
    master = sys.argv[2]
    value = sys.argv[3]
    layers = int(sys.argv[4]) if len(sys.argv) >= 5 else None
    
    if layers:
        ok = set_secret_cli(alias, value, master, layers=layers)
    else:
        ok = set_secret_cli(alias, value, master)
    
    if ok:
        print("Saved:", alias)
        sys.exit(0)
    else:
        print("Failed to save:", alias)
        sys.exit(1)
