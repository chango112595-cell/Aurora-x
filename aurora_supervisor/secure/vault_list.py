#!/usr/bin/env python3
"""
CLI to list all secret aliases in the ASE-∞ vault
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ase_vault import list_secrets

if __name__ == "__main__":
    secrets = list_secrets()
    print(json.dumps(secrets))
