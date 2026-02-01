# Required Environment Variables

## Critical (Server Will Fail Without These)

### `JWT_SECRET`
- **Required:** Yes (throws error if missing)
- **Purpose:** Signing and verifying JWT tokens
- **Generate:** `openssl rand -hex 32` or `node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"`
- **Example:** `JWT_SECRET=abc123def456...`

### `ADMIN_PASSWORD`
- **Required:** Yes (admin login disabled if missing)
- **Purpose:** Admin user password for `/api/auth/login`
- **Generate:** Strong password (min 12 chars, mixed case, numbers, symbols)
- **Example:** `ADMIN_PASSWORD=MySecureP@ssw0rd123!`

### `AURORA_ADMIN_KEY`
- **Required:** Yes (returns 500 if missing)
- **Purpose:** Authentication for `/api/control` and vault endpoints
- **Generate:** `openssl rand -hex 32` or `node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"`
- **Example:** `AURORA_ADMIN_KEY=xyz789abc123...`

### `AURORA_MASTER_PASSPHRASE`
- **Required:** Yes (vault operations fail if missing)
- **Purpose:** Master passphrase for vault encryption/decryption
- **Generate:** Strong passphrase (min 16 chars)
- **Example:** `AURORA_MASTER_PASSPHRASE=MyVerySecureMasterPassphrase123!`

## Optional (Have Defaults)

### `PORT`
- **Default:** `5000`
- **Purpose:** Server listening port
- **Example:** `PORT=5000`

### `NODE_ENV`
- **Default:** `development`
- **Purpose:** Environment mode (affects error handling, admin password requirements)
- **Values:** `development`, `production`
- **Example:** `NODE_ENV=production`

### `AURORA_API_KEY`
- **Default:** None (optional)
- **Purpose:** General API authentication (if used)
- **Example:** `AURORA_API_KEY=optional-api-key`

### `AURORA_AUTO_START`
- **Default:** `true` (if not set to "0" or "false")
- **Purpose:** Auto-start auxiliary services
- **Values:** `true`, `false`, `0`, `1`
- **Example:** `AURORA_AUTO_START=true`

## Bootstrap Template

Create `.env.local` (already in `.gitignore`):

```bash
# Critical - Required
JWT_SECRET=your-generated-secret-here
ADMIN_PASSWORD=your-strong-password-here
AURORA_ADMIN_KEY=your-generated-admin-key-here
AURORA_MASTER_PASSPHRASE=your-strong-master-passphrase-here

# Optional
PORT=5000
NODE_ENV=development
AURORA_AUTO_START=true
```

## Validation Script

Run this to verify all required vars are set:

```bash
# Linux/Mac
required_vars=("JWT_SECRET" "ADMIN_PASSWORD" "AURORA_ADMIN_KEY" "AURORA_MASTER_PASSPHRASE")
for var in "${required_vars[@]}"; do
  if [ -z "${!var}" ]; then
    echo "ERROR: $var is not set"
    exit 1
  else
    echo "✅ $var is set"
  fi
done
echo "All required environment variables are set"

# PowerShell
$required = @("JWT_SECRET", "ADMIN_PASSWORD", "AURORA_ADMIN_KEY", "AURORA_MASTER_PASSPHRASE")
foreach ($var in $required) {
  if (-not $env:$var) {
    Write-Host "ERROR: $var is not set" -ForegroundColor Red
    exit 1
  } else {
    Write-Host "✅ $var is set" -ForegroundColor Green
  }
}
Write-Host "All required environment variables are set" -ForegroundColor Green
```
