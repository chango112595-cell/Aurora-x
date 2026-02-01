# Quick Runtime Test Commands

**Purpose:** Fast verification of P0 security fixes (run these after starting server)

## Prerequisites

1. Server running: `npm run dev` (or your start command)
2. Server port: Default is `5000` (adjust if different)
3. `.env.local` configured with all secrets

## Quick Test Sequence

### Test 1: Server Fails Without JWT_SECRET

```powershell
# In a NEW terminal (keep server running in another)
cd C:\Users\negry\Aurora-x
$env:JWT_SECRET = $null
node server/index.ts
```

**Expected:** ❌ Server fails with error: `"JWT_SECRET is required"`

---

### Test 2: /api/control - No Auth

```powershell
curl -i -X POST http://localhost:5000/api/control `
  -H "Content-Type: application/json" `
  -d '{\"action\":\"status\"}'
```

**Expected:** ✅ **401 Unauthorized** or **403 Forbidden**

---

### Test 3: /api/control - Invalid Auth

```powershell
curl -i -X POST http://localhost:5000/api/control `
  -H "Authorization: Bearer invalid-key-12345" `
  -H "Content-Type: application/json" `
  -d '{\"action\":\"status\"}'
```

**Expected:** ✅ **401 Unauthorized**

---

### Test 4: /api/control - Valid Auth (Localhost)

```powershell
# Get AURORA_ADMIN_KEY from .env.local first
$adminKey = "d481c5de54138586e3bf325bd6cbf39b24bcac1abed05824834f30cc7eced16a"

curl -i -X POST http://localhost:5000/api/control `
  -H "Authorization: Bearer $adminKey" `
  -H "Content-Type: application/json" `
  -d '{\"action\":\"status\"}'
```

**Expected:** ✅ **200 OK** with JSON response

---

### Test 5: /api/control - Invalid Action

```powershell
$adminKey = "d481c5de54138586e3bf325bd6cbf39b24bcac1abed05824834f30cc7eced16a"

curl -i -X POST http://localhost:5000/api/control `
  -H "Authorization: Bearer $adminKey" `
  -H "Content-Type: application/json" `
  -d '{\"action\":\"delete_everything\"}'
```

**Expected:** ✅ **400 Bad Request** (action not in allowlist)

---

### Test 6: Vault - No Auth

```powershell
curl -i http://localhost:5000/api/vault/aliases
```

**Expected:** ✅ **401 Unauthorized**

---

### Test 7: Vault - Query Param (Should Fail)

```powershell
curl -i "http://localhost:5000/api/vault/aliases?key=some-key"
```

**Expected:** ✅ **401 Unauthorized** (query params no longer supported)

---

### Test 8: Vault - Valid Header Auth

```powershell
$adminKey = "d481c5de54138586e3bf325bd6cbf39b24bcac1abed05824834f30cc7eced16a"

curl -i http://localhost:5000/api/vault/aliases `
  -H "x-api-key: $adminKey"
```

**Expected:** ✅ **200 OK** with JSON response

---

### Test 9: Admin Login - Missing Password

```powershell
# Unset ADMIN_PASSWORD temporarily
$oldPass = $env:ADMIN_PASSWORD
$env:ADMIN_PASSWORD = $null

curl -i -X POST http://localhost:5000/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"username\":\"admin\",\"password\":\"any\"}'

# Restore
$env:ADMIN_PASSWORD = $oldPass
```

**Expected:** ✅ **403 Forbidden** or **500 Internal Server Error**

---

### Test 10: Admin Login - Invalid Password

```powershell
curl -i -X POST http://localhost:5000/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"username\":\"admin\",\"password\":\"wrong-password\"}'
```

**Expected:** ✅ **401 Unauthorized** with "Invalid credentials"

---

## Quick Results Template

Copy this and fill in:

```
Test 1 (No JWT_SECRET): ✅ PASS / ❌ FAIL
Test 2 (/api/control no auth): ✅ PASS / ❌ FAIL - Status: ___
Test 3 (/api/control invalid auth): ✅ PASS / ❌ FAIL - Status: ___
Test 4 (/api/control valid auth): ✅ PASS / ❌ FAIL - Status: ___
Test 5 (/api/control invalid action): ✅ PASS / ❌ FAIL - Status: ___
Test 6 (Vault no auth): ✅ PASS / ❌ FAIL - Status: ___
Test 7 (Vault query param): ✅ PASS / ❌ FAIL - Status: ___
Test 8 (Vault header auth): ✅ PASS / ❌ FAIL - Status: ___
Test 9 (Admin login missing password): ✅ PASS / ❌ FAIL - Status: ___
Test 10 (Admin login invalid password): ✅ PASS / ❌ FAIL - Status: ___

Overall: ✅ ALL PASS / ❌ SOME FAIL
```
