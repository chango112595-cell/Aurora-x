#!/usr/bin/env python3
"""
Test script to verify ASE-infinity Vault 22-layer encryption implementation
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from aurora_supervisor.secure.ase_vault import (
    encrypt_secret,
    decrypt_secret,
    set_secret_cli,
    get_secret_cli,
    DEFAULT_LAYERS,
)


def test_vault_22_layers():
    """Test that vault encryption uses 22 layers"""
    print("=" * 60)
    print("ASE-infinity Vault 22-Layer Encryption Test")
    print("=" * 60)

    # Test parameters
    test_passphrase = "test_master_passphrase_12345"
    test_secret = "This is a test secret that should be encrypted with 22 layers"

    print(f"\n1. Testing encryption with {DEFAULT_LAYERS} layers...")
    encrypted = encrypt_secret(test_passphrase, test_secret.encode("utf-8"), layers=DEFAULT_LAYERS)

    if not encrypted:
        print("   [FAIL] Encryption returned None")
        return False

    print(f"   [OK] Encryption successful")
    print(f"   Encrypted length: {len(encrypted)} characters")

    # Parse the encrypted entry to verify layers
    import base64
    import json

    try:
        parts = encrypted.split(".")
        if len(parts) != 3:
            print(f"   [FAIL] Invalid encrypted format (expected 3 parts, got {len(parts)})")
            return False

        header_b64, payload_b64, mac_b64 = parts
        header = json.loads(base64.b64decode(header_b64).decode())

        layer_count = len(header.get("layers", []))
        print(f"   Layer count in header: {layer_count}")

        if layer_count != DEFAULT_LAYERS:
            print(f"   [FAIL] Expected {DEFAULT_LAYERS} layers, got {layer_count}")
            return False

        print(f"   [OK] Verified {layer_count} layers in encryption")

        # Check layer algorithms
        algorithms = [layer.get("alg") for layer in header.get("layers", [])]
        unique_algs = set(algorithms)
        print(f"   Algorithms used: {unique_algs}")
        print(f"   Expected algorithms: AESGCM, CHACHA, SECRETBOX, CHAOSXOR")

        if not all(alg in ["AESGCM", "CHACHA", "SECRETBOX", "CHAOSXOR"] for alg in algorithms):
            print(f"   [WARNING] Unexpected algorithm found")

    except Exception as e:
        print(f"   [FAIL] Error parsing encrypted data: {e}")
        return False

    print(f"\n2. Testing decryption...")
    decrypted = decrypt_secret(test_passphrase, encrypted)

    if not decrypted:
        print("   [FAIL] Decryption returned None")
        return False

    decrypted_text = decrypted.decode("utf-8")

    if decrypted_text != test_secret:
        print(f"   [FAIL] Decrypted text doesn't match original")
        print(f"   Original: {test_secret}")
        print(f"   Decrypted: {decrypted_text}")
        return False

    print(f"   [OK] Decryption successful")
    print(f"   Decrypted text matches original")

    print(f"\n3. Testing vault CLI functions...")
    test_alias = "test_secret_22_layers"

    # Set secret
    result = set_secret_cli(test_alias, test_secret, test_passphrase, layers=DEFAULT_LAYERS)
    if not result:
        print("   [FAIL] Failed to set secret")
        return False

    print(f"   [OK] Secret set successfully")

    # Get secret
    retrieved = get_secret_cli(test_alias, test_passphrase)
    if not retrieved:
        print("   [FAIL] Failed to retrieve secret")
        return False

    if retrieved != test_secret:
        print(f"   [FAIL] Retrieved secret doesn't match")
        return False

    print(f"   [OK] Secret retrieved successfully")

    print(f"\n4. Testing with wrong passphrase...")
    wrong_decrypted = decrypt_secret("wrong_passphrase", encrypted)
    if wrong_decrypted is not None:
        print("   [FAIL] Decryption with wrong passphrase should fail")
        return False

    print(f"   [OK] Wrong passphrase correctly rejected")

    print("\n" + "=" * 60)
    print("[OK] ALL TESTS PASSED")
    print("[OK] Vault 22-layer encryption is working correctly")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = test_vault_22_layers()
    sys.exit(0 if success else 1)
