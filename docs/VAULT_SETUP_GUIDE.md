# ASE-∞ Vault Setup Guide

## Overview

The ASE-∞ (Aurora Secure Encryption - Infinite) Vault is Aurora's built-in system for securely storing API keys and secrets. It uses 22 layers of encryption with multiple algorithms (AES-GCM, ChaCha20-Poly1305, NaCl SecretBox, Chaotic XOR).

Secrets are stored in: `aurora_supervisor/secure/secret_vault.json`

---

## How It Works

1. You choose a **master passphrase** - this is the key to encrypt/decrypt all your secrets
2. Secrets are encrypted with 22+ layers of different algorithms
3. Each secret is stored under an **alias** (a name you choose, like `openai-key`)
4. To retrieve a secret, you need the alias + your master passphrase

---

## Step 1: Navigate to the Vault Directory

Open the Shell and run:

```bash
cd aurora_supervisor/secure
```

**Important:** Make sure you type `cd` (change directory), not `cs`. If you see "cs: command not installed", press Ctrl+C to cancel and retype with `cd`.

---

## Step 2: Store Your First API Key

Run:

```bash
python3 vault_set.py my-api-key MyMasterPassphrase123
```

Then paste your API key when prompted and press Enter.

**Parameters:**
- `my-api-key` = the alias (name) for this secret
- `MyMasterPassphrase123` = your master passphrase (you choose this, remember it!)

**Example - storing an OpenAI key:**
```bash
python3 vault_set.py openai-key MySecretPass2024
# When prompted, paste: sk-proj-abc123...
```

---

## Step 3: Retrieve a Stored Secret

```bash
python3 vault_read.py openai-key MySecretPass2024
```

This prints the decrypted API key.

---

## Step 4: List All Stored Secrets

```bash
python3 vault_list.py
```

This shows all the aliases you've stored (but not the actual values).

---

## Using the Web Interface

### Access the Vault Page

1. Start Aurora (`./aurora-start`)
2. Go to `/vault` in your browser

### What You'll See

- **Vault Status** - Shows if the vault is configured
- **Request Unlock tab** - Request access to a secret
- **Admin Approvals tab** - Approve unlock requests (requires admin key)
- **Operation Log tab** - View all vault operations

---

## Advanced: Non-Interactive Mode

For scripts/automation, use:

```bash
python3 vault_set_noninteractive.py <alias> <passphrase> <secret_value> [layers]
```

**Example:**
```bash
python3 vault_set_noninteractive.py discord-token MyPass123 "MTk4NjIyNDg..." 22
```

---

## Advanced: Custom Encryption Layers

By default, the vault uses 22 encryption layers. You can increase this:

```bash
python3 vault_set.py my-secret MyPassphrase 30
```

This uses 30 layers instead of 22.

---

## API Endpoints (For Programmatic Access)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/vault/health` | GET | Check vault status |
| `/api/vault/unlock-request` | POST | Request to unlock a secret |
| `/api/vault/approve` | POST | Approve an unlock request (admin) |
| `/api/vault/aliases` | GET | List all secret aliases (admin) |
| `/api/vault/requests` | GET | View operation log (admin) |

---

## Environment Variables (Optional)

If you want to use the web API endpoints, you can set these:

| Variable | Purpose |
|----------|---------|
| `AURORA_MASTER_PASSPHRASE` | Pre-set passphrase for API calls |
| `AURORA_ADMIN_KEY` | Admin API key for approval endpoints |

These are optional - you can always use the CLI directly with your passphrase.

---

## File Locations

| File | Purpose |
|------|---------|
| `aurora_supervisor/secure/secret_vault.json` | Encrypted secrets storage |
| `aurora_supervisor/secure/vault_oplog.jsonl` | Operation audit log |
| `aurora_supervisor/secure/vault_set.py` | CLI to store secrets |
| `aurora_supervisor/secure/vault_read.py` | CLI to read secrets |
| `aurora_supervisor/secure/vault_list.py` | CLI to list aliases |
| `aurora_supervisor/secure/ase_vault.py` | Core encryption logic |

---

## Quick Reference

```bash
# Store a secret
cd aurora_supervisor/secure
python3 vault_set.py <alias> <your-passphrase>
# Then paste the secret value

# Read a secret
python3 vault_read.py <alias> <your-passphrase>

# List all secrets
python3 vault_list.py
```

---

## Important Notes

1. **Remember your passphrase** - If you forget it, you cannot recover your secrets
2. **Same passphrase for all secrets** - Use the same master passphrase for all your stored secrets
3. **Secrets are stored locally** - In `aurora_supervisor/secure/secret_vault.json`
4. **Machine-bound** - Secrets include a machine fingerprint, so they work best on the same machine they were created on
