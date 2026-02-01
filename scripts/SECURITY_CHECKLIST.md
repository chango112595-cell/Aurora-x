# Aurora-X Security Checklist (Cursor Fix List)

Verification status after code fixes on `vs-code-aurora-version`. Run greps below to re-verify after changes.

---

## 1. Server crash on handled errors

**Status:** PASS  
**Location:** `server/index.ts`  
**Fix:** Handled errors are logged and not re-thrown; server does not crash.

---

## 2. Hardcoded admin password fallback

**Status:** PASS  
**Location:** `server/users.ts`  
**Fix:** `ADMIN_PASSWORD` is required; no fallback. The literal "Alebec95!" appears only in the *rejection* list (so setting it is refused) and in `server/security-validator.ts` as the *detected* insecure default (startup fails if used).

---

## 3. Vault authentication

**Status:** PASS  
**Location:** `server/routes-vault.ts`  
**Fix:** No `api_key`/`apiKey` query params; auth via `Authorization: Bearer` or `x-api-key` header only; timing-safe comparison for `AURORA_ADMIN_KEY`.

**Verify:** `grep -r "timingSafeEqual" server/`

---

## 4. Client localStorage admin key persistence

**Status:** PASS  
**Location:** `client/src/pages/vault.tsx`, `client/src/pages/settings.tsx`  
**Fix:** Admin key stored in memory only; not persisted to localStorage.

---

## 5. `/api/control` endpoint safety

**Status:** PASS  
**Location:** `server/routes.ts`  
**Fix:** Admin auth, localhost restriction, action allowlist; `spawn` used instead of `execSync`.

---

## 6. Secrets in git history (`.env.local`)

**Status:** PENDING (BFG workflow)  
**Fix:** `.env.local` is in `.gitignore`. To remove from history, use BFG (see `BFG_CHECKLIST.md` and `bfg-purge-env-local.ps1`).  
**Prerequisites:** Java installed; `bfg.jar` at `C:\Users\negry\bfg.jar`; rotate all secrets first; disable branch protection temporarily.

---

## 7. API logs leaking sensitive data

**Status:** PASS  
**Location:** `server/index.ts`, `server/auth-integration.ts` (example)  
**Fix:** Response bodies are not logged; only method, path, status, duration.

---

## 8. JWT secret fallback

**Status:** PASS  
**Location:** `server/auth.ts`  
**Fix:** In production, `JWT_SECRET` must be set explicitly; startup fails if not.

---

## BFG workflow (purge `.env.local` from history)

1. **Rotate secrets** (AURORA_ADMIN_KEY, ADMIN_PASSWORD, JWT_SECRET, etc.).
2. **Notify team** — send contents of `scripts/TEAM_MESSAGE.txt`.
3. **Disable branch protection** on GitHub (Settings → Branches).
4. **Install Java** (e.g. `winget install EclipseAdoptium.Temurin.17.JDK`).
5. **Download BFG** — save as `C:\Users\negry\bfg.jar` from https://rtyley.github.io/bfg-repo-cleaner/.
6. **Run:** `cd C:\Users\negry\Aurora-x\scripts` then `.\bfg-purge-env-local.ps1`.
7. **Re-enable branch protection**; notify team to re-clone or hard-reset.

Full steps: `scripts/BFG_CHECKLIST.md`.
