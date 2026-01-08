#!/usr/bin/env python3
"""
vault_read.py <key>
Reads and decrypts a secret from the encrypted vault
Returns plaintext to stdout for use by Node.js server
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))


def main():
    if len(sys.argv) < 2:
        print("usage: vault_read.py <key>", file=sys.stderr)
        sys.exit(2)

    key = sys.argv[1]

    try:
        from aurora_supervisor.aurora_autonomous_roadmap import get_secret

        value = get_secret(key)
        if value:
            print(value, end="")
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
