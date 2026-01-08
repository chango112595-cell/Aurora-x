#!/usr/bin/env python3
"""
ASE-∞ Vault core (multi-layer encryption/decryption)
- Uses Argon2id key stretching, AEADs (AESGCM / ChaCha20-Poly1305),
  PyNaCl SecretBox, and a deterministic chaotic layer.
- Default layer count ~22 (configurable).
- Vault storage: aurora_supervisor/secure/secret_vault.json
- Operation log: aurora_supervisor/secure/vault_oplog.jsonl
"""

import base64
import json
import os
import secrets
import struct
import time
from pathlib import Path

try:
    import blake3 as _blake3

    HAS_BLAKE3 = True
except Exception:
    _blake3 = None
    HAS_BLAKE3 = False

import nacl.secret
import nacl.utils
from argon2.low_level import Type, hash_secret_raw
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

ROOT = Path(__file__).resolve().parents[2]
SECURE_DIR = ROOT / "aurora_supervisor" / "secure"
VAULT_PATH = SECURE_DIR / "secret_vault.json"
OPLOG = SECURE_DIR / "vault_oplog.jsonl"

DEFAULT_LAYERS = 22
NONCE_AEAD = 12


def _hash_bytes(data: bytes) -> bytes:
    """Hash bytes using blake3 if available, otherwise sha256"""
    if HAS_BLAKE3 and _blake3:
        return _blake3.blake3(data).digest()
    import hashlib

    return hashlib.sha256(data).digest()


def machine_fingerprint() -> bytes:
    """Generate host-binding fingerprint"""
    try:
        import platform

        parts = [
            platform.system(),
            platform.node(),
            platform.machine(),
            platform.platform(),
            str(os.getuid() if hasattr(os, "getuid") else 0),
            str(ROOT),
        ]
    except Exception:
        parts = ["unknown"]
    raw = "|".join(parts).encode("utf-8")
    return _hash_bytes(raw)


def derive_master_seed(passphrase: str, salt: bytes | None = None) -> bytes:
    """KDF: Argon2id key derivation"""
    salt = salt or machine_fingerprint()
    seed = hash_secret_raw(
        passphrase.encode("utf-8"),
        salt,
        time_cost=3,
        memory_cost=65536,
        parallelism=2,
        hash_len=64,
        type=Type.ID,
    )
    return seed


def per_layer_key(master_seed: bytes, layer_index: int) -> bytes:
    """Derive per-layer key from master seed"""
    if HAS_BLAKE3 and _blake3:
        h = _blake3.blake3()
        h.update(master_seed)
        h.update(b"::layer::")
        h.update(struct.pack(">I", layer_index))
        return h.digest()[:32]
    import hashlib

    return hashlib.sha256(master_seed + struct.pack(">I", layer_index)).digest()[:32]


def chaotic_stream(seed: bytes, length: int) -> bytes:
    """Deterministic chaotic stream generator"""
    out = bytearray()
    counter = 0
    state = int.from_bytes((seed[:16] if len(seed) >= 16 else seed.ljust(16, b"\0")), "big")
    while len(out) < length:
        state = (1103515245 * state + 12345) & ((1 << 128) - 1)
        chunk = state.to_bytes(16, "big") + struct.pack(">I", counter)
        h = _hash_bytes(chunk)
        out += h
        counter += 1
    return bytes(out[:length])


def aesgcm_encrypt(key: bytes, plaintext: bytes):
    nonce = secrets.token_bytes(NONCE_AEAD)
    aes = AESGCM(key)
    ct = aes.encrypt(nonce, plaintext, None)
    return {"alg": "AESGCM", "nonce": nonce, "ct": ct}


def aesgcm_decrypt(key: bytes, nonce: bytes, ct: bytes):
    aes = AESGCM(key)
    return aes.decrypt(nonce, ct, None)


def chacha_encrypt(key: bytes, plaintext: bytes):
    nonce = secrets.token_bytes(NONCE_AEAD)
    ch = ChaCha20Poly1305(key)
    ct = ch.encrypt(nonce, plaintext, None)
    return {"alg": "CHACHA", "nonce": nonce, "ct": ct}


def chacha_decrypt(key: bytes, nonce: bytes, ct: bytes):
    ch = ChaCha20Poly1305(key)
    return ch.decrypt(nonce, ct, None)


def secretbox_encrypt(key: bytes, plaintext: bytes):
    box = nacl.secret.SecretBox(key[:32])
    nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
    ct = box.encrypt(plaintext, nonce)
    return {"alg": "SECRETBOX", "ct": ct}


def secretbox_decrypt(key: bytes, ct: bytes):
    box = nacl.secret.SecretBox(key[:32])
    return box.decrypt(ct)


def encrypt_secret(
    master_passphrase: str, secret_bytes: bytes, layers: int = DEFAULT_LAYERS
) -> str:
    """Multi-layer encryption with random algorithm selection per layer"""
    master_seed = derive_master_seed(master_passphrase)
    payload = secret_bytes
    header = {
        "version": "ASE-1",
        "layers": [],
        "machine": base64.b64encode(machine_fingerprint()).decode(),
    }

    for i in range(layers):
        k = per_layer_key(master_seed, i)
        choice = secrets.randbelow(4)

        if choice == 0:
            enc = aesgcm_encrypt(k, payload)
            payload = enc["nonce"] + enc["ct"]
        elif choice == 1:
            enc = chacha_encrypt(k, payload)
            payload = enc["nonce"] + enc["ct"]
        elif choice == 2:
            enc = secretbox_encrypt(k, payload)
            payload = enc["ct"]
        else:
            stream = chaotic_stream(k + struct.pack(">I", i), len(payload))
            payload = bytes(x ^ y for x, y in zip(payload, stream))
            enc = {"alg": "CHAOSXOR"}

        header["layers"].append({"index": i, "alg": enc["alg"]})

    mac = _hash_bytes(master_seed + payload)

    jheader = json.dumps(header, separators=(",", ":")).encode()
    entry = (
        base64.b64encode(jheader).decode()
        + "."
        + base64.b64encode(payload).decode()
        + "."
        + base64.b64encode(mac).decode()
    )

    SECURE_DIR.mkdir(parents=True, exist_ok=True)
    with open(OPLOG, "a") as f:
        f.write(json.dumps({"ts": time.time(), "op": "encrypt", "layers": layers}) + "\n")

    return entry


def decrypt_secret(master_passphrase: str, entry: str) -> bytes | None:
    """Decrypt multi-layer encrypted secret"""
    try:
        master_seed = derive_master_seed(master_passphrase)
        header_b64, payload_b64, mac_b64 = entry.split(".")
        header = json.loads(base64.b64decode(header_b64).decode())
        payload = base64.b64decode(payload_b64)
        mac = base64.b64decode(mac_b64)

        check = _hash_bytes(master_seed + payload)

        if check != mac:
            raise ValueError("MAC mismatch")

        current = payload
        for layer in reversed(header.get("layers", [])):
            idx = layer["index"]
            k = per_layer_key(master_seed, idx)
            alg = layer["alg"]

            if alg == "AESGCM":
                nonce = current[:NONCE_AEAD]
                ct = current[NONCE_AEAD:]
                current = aesgcm_decrypt(k, nonce, ct)
            elif alg == "CHACHA":
                nonce = current[:NONCE_AEAD]
                ct = current[NONCE_AEAD:]
                current = chacha_decrypt(k, nonce, ct)
            elif alg == "SECRETBOX":
                current = secretbox_decrypt(k, current)
            elif alg == "CHAOSXOR":
                stream = chaotic_stream(k + struct.pack(">I", idx), len(current))
                current = bytes(x ^ y for x, y in zip(current, stream))
            else:
                raise ValueError("Unknown layer")

        with open(OPLOG, "a") as f:
            f.write(
                json.dumps(
                    {"ts": time.time(), "op": "decrypt", "layers": len(header.get("layers", []))}
                )
                + "\n"
            )

        return current
    except Exception as e:
        with open(OPLOG, "a") as f:
            f.write(json.dumps({"ts": time.time(), "op": "decrypt_error", "error": str(e)}) + "\n")
        return None


def vault_load() -> dict[str, str]:
    """Load vault from disk"""
    if not VAULT_PATH.exists():
        return {}
    try:
        return json.load(open(VAULT_PATH))
    except:
        return {}


def vault_save_all(v: dict[str, str]):
    """Save vault to disk"""
    SECURE_DIR.mkdir(parents=True, exist_ok=True)
    json.dump(v, open(VAULT_PATH, "w"), indent=2)


def set_secret_cli(
    alias: str, plaintext: str, master_passphrase: str, layers: int = DEFAULT_LAYERS
):
    """Set a secret in the vault"""
    v = vault_load()
    entry = encrypt_secret(master_passphrase, plaintext.encode("utf-8"), layers=layers)
    v[alias] = entry
    vault_save_all(v)
    return True


def get_secret_cli(alias: str, master_passphrase: str) -> str | None:
    """Get a secret from the vault"""
    v = vault_load()
    entry = v.get(alias)
    if not entry:
        return None
    pt = decrypt_secret(master_passphrase, entry)
    return pt.decode("utf-8") if pt else None


def list_secrets() -> list:
    """List all secret aliases in the vault"""
    v = vault_load()
    return list(v.keys())


def delete_secret(alias: str) -> bool:
    """Delete a secret from the vault"""
    v = vault_load()
    if alias in v:
        del v[alias]
        vault_save_all(v)
        return True
    return False
