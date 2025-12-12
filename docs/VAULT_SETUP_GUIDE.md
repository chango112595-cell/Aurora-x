# ASE-∞ Vault Setup Guide

## Overview

The ASE-∞ (Aurora Secure Encryption - Infinite) Vault provides multi-layer encryption for storing sensitive secrets like API keys, tokens, and credentials. It uses 22+ layers of encryption by default with algorithms including AES-GCM, ChaCha20-Poly1305, and NaCl SecretBox.

---

## Step 1: Set Required Environment Variables

Before using the vault, you must configure two environment variables in Replit's Secrets tool.

### How to Access Secrets in Replit

1. Look at the left side of your Replit workspace
2. Click **"All tools"** (or use the search bar at the top)
3. Select **"Secrets"** from the list
4. You'll see the Secrets management panel

### Required Secrets

Add these two secrets:

| Key | Description | Example Value |
|-----|-------------|---------------|
| `AURORA_MASTER_PASSPHRASE` | Master passphrase used to encrypt/decrypt all vault secrets. Choose a strong, memorable passphrase. | `MySecure-Passphrase-2024!` |
| `AURORA_ADMIN_KEY` | Admin API key for approving vault unlock requests. Generate a random string. | `admin-key-abc123xyz789` |

### Adding a Secret

1. Click the **"+ New Secret"** button
2. Enter the **Key** (e.g., `AURORA_MASTER_PASSPHRASE`)
3. Enter the **Value** (your chosen passphrase or key)
4. Click **"Add Secret"**
5. Repeat for the second secret

---

## Step 2: Verify Vault Health

After setting the environment variables, verify the vault is configured correctly.

### Option A: Using the API

Open a browser or use curl:

```
GET https://your-replit-url/api/vault/health
```

Expected response when configured:
```json
{
  "status": "configured",
  "hasPassphrase": true,
  "hasAdminKey": true
}
```

### Option B: Using the Frontend

1. Navigate to `/vault` in your browser
2. The vault dashboard will show the configuration status
3. Green indicators mean everything is set up correctly

---

## Step 3: Using the Vault

### Storing a Secret (CLI)

Open the Shell in Replit and run:

```bash
cd aurora_supervisor/secure
python3 vault_set.py <alias> <your_master_passphrase> [layers]
```

**Parameters:**
- `<alias>`: A name for your secret (e.g., `openai-api-key`)
- `<your_master_passphrase>`: Your `AURORA_MASTER_PASSPHRASE` value
- `[layers]`: Optional - number of encryption layers (default: 22)

**Example:**
```bash
python3 vault_set.py openai-key MySecure-Passphrase-2024!
# Then enter your secret value when prompted
```

### Non-Interactive Mode

For automation, use the non-interactive script:

```bash
python3 vault_set_noninteractive.py <alias> <master_passphrase> <secret_value> [layers]
```

### Reading a Secret (CLI)

```bash
cd aurora_supervisor/secure
python3 vault_read.py <alias> <your_master_passphrase>
```

**Example:**
```bash
python3 vault_read.py openai-key MySecure-Passphrase-2024!
```

### Listing All Secrets (CLI)

```bash
cd aurora_supervisor/secure
python3 vault_list.py
```

This shows all stored secret aliases (not the actual values).

---

## Step 4: Using the Web Interface

### Accessing the Vault UI

Navigate to `/vault` in your browser to access the visual interface.

### Requesting a Secret Unlock

1. Go to `/vault`
2. Enter the **alias** of the secret you need
3. Enter your **master passphrase**
4. Click **"Request Unlock"**
5. The request is logged for audit purposes

### Admin Approval (For Sensitive Operations)

If admin approval is required:

1. Go to `/vault`
2. Enter your **Admin Key** (`AURORA_ADMIN_KEY` value)
3. View pending requests in the admin panel
4. Click **"Approve"** to retrieve the decrypted secret

---

## API Reference

### Check Vault Health
```
GET /api/vault/health
```
Returns configuration status.

### Request Secret Unlock
```
POST /api/vault/unlock-request
Content-Type: application/json

{
  "alias": "my-secret-name",
  "passphrase": "your-master-passphrase"
}
```

### Approve and Retrieve Secret (Admin Only)
```
POST /api/vault/approve
Content-Type: application/json

{
  "alias": "my-secret-name",
  "passphrase": "your-master-passphrase",
  "adminKey": "your-admin-key"
}
```

### List Secret Aliases (Admin Only)
```
GET /api/vault/aliases?adminKey=your-admin-key
```

### View Operation Log (Admin Only)
```
GET /api/vault/requests?adminKey=your-admin-key
```

---

## Security Best Practices

1. **Choose a strong master passphrase**: Use a combination of words, numbers, and symbols. At least 16 characters recommended.

2. **Keep your admin key private**: Only share with trusted administrators.

3. **Don't commit secrets to git**: The vault stores encrypted data in `aurora_supervisor/secure/vault_data/` which should be in `.gitignore`.

4. **Use different passphrases for different environments**: Development and production should have separate master passphrases.

5. **Regularly rotate secrets**: Periodically update stored secrets and the master passphrase.

---

## Troubleshooting

### "Vault not configured" Error

**Cause**: Missing environment variables.

**Solution**: 
1. Go to Secrets tool in Replit
2. Verify both `AURORA_MASTER_PASSPHRASE` and `AURORA_ADMIN_KEY` are set
3. Restart the application workflow

### "Decryption failed" Error

**Cause**: Wrong passphrase or corrupted data.

**Solution**:
1. Verify you're using the correct master passphrase
2. Check that the secret alias exists with `python3 vault_list.py`

### "Unauthorized" Error on Admin Endpoints

**Cause**: Invalid or missing admin key.

**Solution**:
1. Verify your `AURORA_ADMIN_KEY` is set correctly
2. Ensure you're passing the correct admin key in requests

---

## File Locations

| File | Purpose |
|------|---------|
| `aurora_supervisor/secure/ase_vault.py` | Main vault encryption/decryption logic |
| `aurora_supervisor/secure/vault_set.py` | CLI tool to store secrets |
| `aurora_supervisor/secure/vault_read.py` | CLI tool to read secrets |
| `aurora_supervisor/secure/vault_list.py` | CLI tool to list secret aliases |
| `aurora_supervisor/secure/vault_data/` | Encrypted secret storage (auto-created) |
| `server/routes-vault.ts` | Backend API routes |
| `server/vault-bridge.ts` | TypeScript-to-Python bridge |
| `client/src/pages/vault.tsx` | Frontend vault UI |

---

## Quick Start Checklist

- [ ] Set `AURORA_MASTER_PASSPHRASE` in Replit Secrets
- [ ] Set `AURORA_ADMIN_KEY` in Replit Secrets  
- [ ] Restart the application workflow
- [ ] Verify vault health at `/api/vault/health`
- [ ] Access vault UI at `/vault`
- [ ] Store your first secret using CLI or web interface
