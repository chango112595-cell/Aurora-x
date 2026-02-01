# BFG Purge .env.local — Checklist

Follow this order. Do NOT skip rotation.

## 0) Freeze pushes (send to team)

Copy the contents of `TEAM_MESSAGE.txt` and send to anyone who pushes to Aurora-x. Ask them to stop pushing until you say "all clear."

---

## 1) Rotate secrets immediately (do this first)

Rotate these **now** (revoke/regenerate):

- [ ] `AURORA_ADMIN_KEY`
- [ ] `ADMIN_PASSWORD`
- [ ] `JWT_SECRET`
- [ ] Any third-party API keys (Groq, Gemini, DeepSeek, etc.)

Then update:

- [ ] GitHub Actions secrets (Repo → Settings → Secrets and variables → Actions)
- [ ] Your local `.env.local` (keep it untracked; add to .gitignore — already done)
- [ ] Any deployment/server/docker environment variables

---

## 2) Temporarily disable branch protection

- [ ] GitHub → Aurora-x → **Settings** → **Branches**
- [ ] Edit the branch protection rule(s) that apply (e.g. default branch, vs-code-aurora-version if protected)
- [ ] Temporarily **disable** "Prevent force pushes" / or disable the rule
- [ ] Save

---

## 3) Install Java (if not already)

- [ ] Run: `java -version`
- [ ] If it fails: install JRE/JDK (e.g. `winget install EclipseAdoptium.Temurin.17.JDK` or https://adoptium.net/)
- [ ] Restart terminal, run `java -version` again

---

## 4) Run BFG cleanup

- [ ] Ensure `C:\Users\negry\bfg.jar` exists (already downloaded)
- [ ] Run the script:
  ```powershell
  cd C:\Users\negry\Aurora-x\scripts
  .\bfg-purge-env-local.ps1
  ```
- [ ] If the script fails, run the commands manually (see script body)

---

## 5) Verify .env.local is gone

In `C:\Users\negry\aurora-x-mirror.git` (or after a fresh clone):

```powershell
git log --all -- .env.local
```
→ Should return **nothing**.

```powershell
git rev-list --objects --all | findstr /i ".env.local"
```
→ Should return **nothing**.

---

## 6) Re-enable branch protection

- [ ] GitHub → Settings → Branches → re-enable the rule(s) you disabled in step 2

---

## 7) Team cleanup (prevent recontamination)

- [ ] Send "all clear" + contents of `TEAM_MESSAGE.txt` so everyone re-clones or hard-resets

---

## 8) Optional: prevent recurrence

- [ ] `.env.local` is in `.gitignore` (already done)
- [ ] Consider adding secret scanning (e.g. gitleaks, GitHub Advanced Security)
- [ ] Avoid `git add .` on repos with runtime logs/state
