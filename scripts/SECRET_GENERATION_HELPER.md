# Secret Generation Helper

**Generated secrets for rotation** (use these or generate your own):

## Generated Secrets (Ready to Use)

```bash
# JWT Secret (32 bytes = 64 hex chars)
JWT_SECRET=c6f44238bd0e1471ea5fd1785818f5f268ed956f14a6d455c3ec502bcab3a339

# Aurora Admin Key (32 bytes = 64 hex chars)
AURORA_ADMIN_KEY=d481c5de54138586e3bf325bd6cbf39b24bcac1abed05824834f30cc7eced16a
```

## Generate New Secrets (If Needed)

### Using Node.js:
```bash
node -e "console.log('JWT_SECRET=' + require('crypto').randomBytes(32).toString('hex')); console.log('AURORA_ADMIN_KEY=' + require('crypto').randomBytes(32).toString('hex'));"
```

### Using OpenSSL:
```bash
openssl rand -hex 32  # For JWT_SECRET
openssl rand -hex 32  # For AURORA_ADMIN_KEY
```

### Generate ADMIN_PASSWORD:
Use a password manager or generate a strong password:
- Minimum 12 characters
- Mixed case (A-Z, a-z)
- Numbers (0-9)
- Special characters (!@#$%^&*)

### Generate AURORA_MASTER_PASSPHRASE:
Use a strong passphrase:
- Minimum 16 characters
- Can be multiple words with spaces
- Include numbers and special characters

## Quick Setup Template

Create `.env.local` with these values:

```bash
# Critical Secrets (REQUIRED)
JWT_SECRET=c6f44238bd0e1471ea5fd1785818f5f268ed956f14a6d455c3ec502bcab3a339
ADMIN_PASSWORD=YourStrongPassword123!
AURORA_ADMIN_KEY=d481c5de54138586e3bf325bd6cbf39b24bcac1abed05824834f30cc7eced16a
AURORA_MASTER_PASSPHRASE=YourVerySecureMasterPassphrase123!

# Optional
PORT=5000
NODE_ENV=development
AURORA_AUTO_START=true
```

**⚠️ IMPORTANT:** Replace the generated values above with your own, or use the generated ones but ensure you update ALL locations (GitHub Actions, deployments, etc.) with the SAME values.
