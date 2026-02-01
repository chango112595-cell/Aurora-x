# Secret Rotation Checklist

**CRITICAL:** Rotate all secrets immediately after `.env.local` history purge, even if the file is removed from git history.

## Required Secrets to Rotate

### 1. Core Authentication Secrets

- [ ] **`JWT_SECRET`** (Required - server will fail without it)
  - Generate new: `openssl rand -hex 32` or `node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"`
  - Update locations:
    - [ ] Local `.env.local` (untracked)
    - [ ] GitHub Actions secrets
    - [ ] Production deployment environment
    - [ ] Development environment
    - [ ] Docker compose files
    - [ ] Kubernetes secrets (if applicable)

- [ ] **`ADMIN_PASSWORD`** (Required for admin login)
  - Generate new strong password (min 12 chars, mixed case, numbers, symbols)
  - Update locations:
    - [ ] Local `.env.local` (untracked)
    - [ ] GitHub Actions secrets
    - [ ] Production deployment environment
    - [ ] Development environment
    - [ ] Docker compose files
    - [ ] Kubernetes secrets (if applicable)

- [ ] **`AURORA_ADMIN_KEY`** (Required for `/api/control` and vault endpoints)
  - Generate new: `openssl rand -hex 32` or `node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"`
  - Update locations:
    - [ ] Local `.env.local` (untracked)
    - [ ] GitHub Actions secrets
    - [ ] Production deployment environment
    - [ ] Development environment
    - [ ] Docker compose files
    - [ ] Kubernetes secrets (if applicable)
    - [ ] Client-side admin tools (if stored)

- [ ] **`AURORA_MASTER_PASSPHRASE`** (Required for vault operations)
  - Generate new strong passphrase (min 16 chars)
  - Update locations:
    - [ ] Local `.env.local` (untracked)
    - [ ] GitHub Actions secrets
    - [ ] Production deployment environment
    - [ ] Development environment
    - [ ] Secure vault storage (if applicable)

### 2. Optional but Recommended

- [ ] **`AURORA_API_KEY`** (If used for API authentication)
  - Generate new if exists
  - Update all API clients

### 3. Third-Party API Keys (Rotate if exposed)

- [ ] **Groq API Key** (if used)
- [ ] **Gemini API Key** (if used)
- [ ] **DeepSeek API Key** (if used)
- [ ] **OpenAI API Key** (if used)
- [ ] **Anthropic API Key** (if used)
- [ ] **Other third-party services**

## Verification Steps

After rotation:

1. [ ] Test server startup with new secrets
2. [ ] Verify admin login works with new `ADMIN_PASSWORD`
3. [ ] Verify `/api/control` works with new `AURORA_ADMIN_KEY`
4. [ ] Verify vault operations work with new `AURORA_MASTER_PASSPHRASE`
5. [ ] Verify JWT token generation works with new `JWT_SECRET`
6. [ ] Test all GitHub Actions workflows (they should use new secrets)
7. [ ] Verify production deployment uses new secrets

## Security Notes

- **Never commit secrets to git** - use `.env.local` (already in `.gitignore`)
- **Use different secrets for dev/staging/production**
- **Store secrets securely** - use GitHub Secrets, environment variables, or secret management tools
- **Document secret locations** - maintain a secure list of where secrets are stored (not in git)

## Post-Rotation Cleanup

- [ ] Revoke old secrets (if service supports revocation)
- [ ] Monitor logs for authentication failures (may indicate old secrets still in use)
- [ ] Update team documentation with new secret management procedures
