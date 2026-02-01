# GitHub Actions Secrets Update Guide

## Steps to Update Secrets

1. **Navigate to GitHub Repository**
   - Go to: `https://github.com/chango112595-cell/Aurora-x`
   - Click: **Settings** (top menu)
   - Click: **Secrets and variables** → **Actions** (left sidebar)

2. **Update Each Secret**

   For each secret below, click **Update** (or **New repository secret** if it doesn't exist):

   ### `JWT_SECRET`
   - **Value:** `c6f44238bd0e1471ea5fd1785818f5f268ed956f14a6d455c3ec502bcab3a339`
   - **Action:** Update or Create

   ### `AURORA_ADMIN_KEY`
   - **Value:** `d481c5de54138586e3bf325bd6cbf39b24bcac1abed05824834f30cc7eced16a`
   - **Action:** Update or Create

   ### `ADMIN_PASSWORD`
   - **Value:** (Use the same strong password you set in `.env.local`)
   - **Action:** Update or Create
   - **⚠️ IMPORTANT:** Must match your local `.env.local` value

   ### `AURORA_MASTER_PASSPHRASE`
   - **Value:** (Use the same strong passphrase you set in `.env.local`)
   - **Action:** Update or Create
   - **⚠️ IMPORTANT:** Must match your local `.env.local` value

3. **Verify Secrets Are Updated**
   - Check that all 4 secrets show "Updated" timestamp
   - Ensure values match your local `.env.local`

4. **Test Workflow (Optional but Recommended)**
   - Push a trivial commit or manually trigger a workflow
   - Verify workflow runs successfully with new secrets
   - Check workflow logs to ensure secrets are accessible

## Checklist

- [ ] `JWT_SECRET` updated in GitHub Actions secrets
- [ ] `AURORA_ADMIN_KEY` updated in GitHub Actions secrets
- [ ] `ADMIN_PASSWORD` updated in GitHub Actions secrets (matches local)
- [ ] `AURORA_MASTER_PASSPHRASE` updated in GitHub Actions secrets (matches local)
- [ ] All third-party API keys rotated (if applicable)
- [ ] Workflow test run successful

## Security Notes

- **Never commit secrets** - They're stored securely in GitHub Secrets
- **Use same values** - Local `.env.local` and GitHub Secrets should match
- **Rotate regularly** - Consider rotating secrets periodically as security best practice
