#!/usr/bin/env python3
"""
Python bridge for reading secrets from the ASE-∞ vault
Node/server will call this to fetch plaintext; returns empty on failure
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ase_vault import get_secret_cli

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: vault_read.py <alias> <master_passphrase>")
        sys.exit(2)

    alias = sys.argv[1]
    master = sys.argv[2]

    val = get_secret_cli(alias, master)

    if val is None:
        print("")
        sys.exit(1)

    print(val)
    sys.exit(0)
