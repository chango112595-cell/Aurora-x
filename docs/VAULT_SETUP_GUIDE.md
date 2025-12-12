# ASE-∞ Vault Setup Guide

## Overview

The ASE-∞ (Aurora Secure Encryption - Infinite) Vault is Aurora's built-in system for securely storing API keys and secrets. It uses 22 layers of encryption with multiple algorithms (AES-GCM, ChaCha20-Poly1305, NaCl SecretBox, Chaotic XOR).

There are **two ways** to use the vault:
- **Web Interface** (Settings page) - Easiest, but requires environment variables
- **Command Line** - More flexible, no environment variables needed

---

## Option A: Web Interface (Recommended)

This is the Settings page UI with "ASE-Infinity Vault - API Key Management".

### Step 1: Set Environment Variables

You need to set two environment variables. In Replit, go to the **Secrets** tool and add:

| Key | What to Enter |
|-----|---------------|
| `AURORA_MASTER_PASSPHRASE` | Choose a strong passphrase (e.g., `MySecurePass2024!`) |
| `AURORA_ADMIN_KEY` | Choose an admin key (e.g., `admin-key-xyz123`) |

### Step 2: Restart the Application

After setting the secrets, restart Aurora:
```bash
./aurora-start
```

Or restart the "Start application" workflow.

### Step 3: Use the Settings Page

1. Go to the **Settings** page in Aurora
2. The vault status should now show **"Configured"**
3. Enter an alias (name) for your API key (e.g., `ADMIN_PASSWORD`)
4. Enter the secret value
5. Click **"Store in Vault"**

### Step 4: View Stored Keys

Your stored API keys will appear in the "Stored API Keys" section on the same page.

---

## Option B: Command Line (No Setup Needed)

Use this if you prefer the terminal or don't want to set environment variables.

### Step 1: Navigate to the Vault Directory

```bash
cd aurora_supervisor/secure
```

**Important:** Type `cd` (change directory), not `cs`. If you see "cs: command not installed", press Ctrl+C and retype with `cd`.

### Step 2: Store an API Key

```bash
python3 vault_set.py <alias> <your-passphrase>
```

When prompted, paste your API key and press Enter.

**Example:**
```bash
python3 vault_set.py openai-key MySecretPass2024
# Paste: sk-proj-abc123...
# Press Enter
```

### Step 3: Retrieve an API Key

```bash
python3 vault_read.py <alias> <your-passphrase>
```

**Example:**
```bash
python3 vault_read.py openai-key MySecretPass2024
```

### Step 4: List All Stored Keys

```bash
python3 vault_list.py
```

---

## Which Option Should I Choose?

| If you want... | Use... |
|----------------|--------|
| Easy visual interface | **Option A** (Web Interface) |
| Quick one-time storage | **Option B** (Command Line) |
| No environment variables | **Option B** (Command Line) |
| Other Aurora services to access keys | **Option A** (Web Interface) |

---

## Environment Variables Reference

| Variable | Required For | Purpose |
|----------|--------------|---------|
| `AURORA_MASTER_PASSPHRASE` | Web Interface | Encrypts/decrypts all secrets |
| `AURORA_ADMIN_KEY` | Web Interface | Admin access for approvals |

These are NOT needed for the command line method.

---

## File Locations

| File | Purpose |
|------|---------|
| `aurora_supervisor/secure/secret_vault.json` | Encrypted secrets storage |
| `aurora_supervisor/secure/vault_oplog.jsonl` | Operation audit log |
| `aurora_supervisor/secure/vault_set.py` | CLI to store secrets |
| `aurora_supervisor/secure/vault_read.py` | CLI to read secrets |
| `aurora_supervisor/secure/vault_list.py` | CLI to list aliases |

---

## Troubleshooting

### "Not Configured" on Settings Page
**Solution:** Set both `AURORA_MASTER_PASSPHRASE` and `AURORA_ADMIN_KEY` in Secrets, then restart Aurora.

### "cs: command not installed"
**Solution:** You typed `cs` instead of `cd`. Press Ctrl+C and type `cd aurora_supervisor/secure`.

### Can't decrypt a secret
**Solution:** Make sure you're using the exact same passphrase you used when storing it.

---

## Important Notes

1. **Remember your passphrase** - If you forget it, you cannot recover your secrets
2. **Same passphrase for all secrets** - Use the same master passphrase consistently
3. **Secrets are stored locally** - In `aurora_supervisor/secure/secret_vault.json`
