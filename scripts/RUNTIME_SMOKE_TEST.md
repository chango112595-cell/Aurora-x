# Runtime Smoke Test Checklist

**Purpose:** Verify P0 security fixes work correctly at runtime.

## Prerequisites

- Server dependencies installed (`npm install`)
- Terminal access to run server and curl commands

## Test 1: Server Fails Fast on Missing Required Secrets

### Test 1a: Missing JWT_SECRET

```bash
# Unset JWT_SECRET
unset JWT_SECRET  # Linux/Mac
# OR
$env:JWT_SECRET = $null  # PowerShell

# Start server
npm run dev
# OR
node server/index.ts
```

**Expected Result:** ✅ Server should **fail to start** with error: `"JWT_SECRET is required"`

**Actual Result:** ________________

---

### Test 1b: Missing ADMIN_PASSWORD (Production Mode)

```bash
# Set production mode
export NODE_ENV=production  # Linux/Mac
# OR
$env:NODE_ENV = "production"  # PowerShell

# Unset ADMIN_PASSWORD
unset ADMIN_PASSWORD  # Linux/Mac
# OR
$env:ADMIN_PASSWORD = $null  # PowerShell

# Start server
npm run dev
```

**Expected Result:** 
- ✅ Production: Server should fail or admin login should return 500/403
- ✅ Development: May allow server start but admin login should be disabled

**Actual Result:** ________________

---

## Test 2: `/api/control` Endpoint Security

### Test 2a: No Authentication

```bash
curl -i -X POST http://localhost:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"action":"status"}'
```

**Expected Result:** ✅ **401 Unauthorized** or **403 Forbidden**

**Actual Result:** ________________

---

### Test 2b: Invalid Authentication

```bash
curl -i -X POST http://localhost:5000/api/control \
  -H "Authorization: Bearer invalid-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"action":"status"}'
```

**Expected Result:** ✅ **401 Unauthorized**

**Actual Result:** ________________

---

### Test 2c: Valid Auth but Not Localhost (Remote Request)

**Note:** This test requires making a request from a non-localhost IP. If testing locally, you can simulate by temporarily modifying the middleware, or test from another machine.

```bash
# From remote machine (replace with your server IP)
curl -i -X POST http://<SERVER_IP>:5000/api/control \
  -H "Authorization: Bearer <VALID_AURORA_ADMIN_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"action":"status"}'
```

**Expected Result:** ✅ **403 Forbidden** (even with valid auth, remote requests blocked)

**Actual Result:** ________________

---

### Test 2d: Valid Auth + Localhost

```bash
# Set AURORA_ADMIN_KEY in your .env.local first
export AURORA_ADMIN_KEY="your-actual-admin-key"  # Linux/Mac
# OR
$env:AURORA_ADMIN_KEY = "your-actual-admin-key"  # PowerShell

curl -i -X POST http://localhost:5000/api/control \
  -H "Authorization: Bearer $AURORA_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"action":"status"}'
```

**Expected Result:** ✅ **200 OK** with JSON response

**Actual Result:** ________________

---

### Test 2e: Invalid Action (Allowlist Test)

```bash
curl -i -X POST http://localhost:5000/api/control \
  -H "Authorization: Bearer $AURORA_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"action":"delete_everything"}'
```

**Expected Result:** ✅ **400 Bad Request** with error message about invalid action

**Actual Result:** ________________

---

## Test 3: Vault Endpoint Security

### Test 3a: No Authentication Header

```bash
curl -i http://localhost:5000/api/vault/aliases
```

**Expected Result:** ✅ **401 Unauthorized**

**Actual Result:** ________________

---

### Test 3b: Query Parameter Auth (Should Fail)

```bash
curl -i "http://localhost:5000/api/vault/aliases?key=some-key"
```

**Expected Result:** ✅ **401 Unauthorized** (query params no longer supported)

**Actual Result:** ________________

---

### Test 3c: Valid Header Auth

```bash
curl -i http://localhost:5000/api/vault/aliases \
  -H "x-api-key: $AURORA_ADMIN_KEY"
```

**Expected Result:** ✅ **200 OK** with JSON response

**Actual Result:** ________________

---

### Test 3d: Bearer Token Auth

```bash
curl -i http://localhost:5000/api/vault/aliases \
  -H "Authorization: Bearer $AURORA_ADMIN_KEY"
```

**Expected Result:** ✅ **200 OK** with JSON response

**Actual Result:** ________________

---

## Test 4: Error Handling (No Server Crashes)

### Test 4a: Invalid JSON in Request Body

```bash
curl -i -X POST http://localhost:5000/api/control \
  -H "Authorization: Bearer $AURORA_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{invalid json}'
```

**Expected Result:** ✅ **400 Bad Request** - Server should NOT crash, should return error response

**Actual Result:** ________________

---

### Test 4b: Check Server Logs

After running tests, check server console output:

**Expected:** 
- ✅ No `throw err` causing uncaught exceptions
- ✅ Error messages logged but server continues running
- ✅ No response body content in logs (only method/path/status/duration)

**Actual:** ________________

---

## Test 5: Admin Login Security

### Test 5a: Missing ADMIN_PASSWORD

```bash
# Unset ADMIN_PASSWORD
unset ADMIN_PASSWORD

curl -i -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"any-password"}'
```

**Expected Result:** 
- ✅ Production: **500 Internal Server Error** or **403 Forbidden**
- ✅ Development: **403 Forbidden** with message "Admin login disabled (set ADMIN_PASSWORD)"

**Actual Result:** ________________

---

### Test 5b: Invalid Admin Password

```bash
# Set ADMIN_PASSWORD
export ADMIN_PASSWORD="correct-password"

curl -i -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrong-password"}'
```

**Expected Result:** ✅ **401 Unauthorized** with message "Invalid credentials"

**Actual Result:** ________________

---

### Test 5c: Valid Admin Password

```bash
curl -i -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"$ADMIN_PASSWORD\"}"
```

**Expected Result:** ✅ **200 OK** with access token and refresh token

**Actual Result:** ________________

---

## Summary

- [ ] Test 1a: JWT_SECRET required ✅/❌
- [ ] Test 1b: ADMIN_PASSWORD required ✅/❌
- [ ] Test 2a: /api/control no auth → 401 ✅/❌
- [ ] Test 2b: /api/control invalid auth → 401 ✅/❌
- [ ] Test 2c: /api/control remote → 403 ✅/❌
- [ ] Test 2d: /api/control localhost + auth → 200 ✅/❌
- [ ] Test 2e: /api/control invalid action → 400 ✅/❌
- [ ] Test 3a: Vault no auth → 401 ✅/❌
- [ ] Test 3b: Vault query param → 401 ✅/❌
- [ ] Test 3c: Vault header auth → 200 ✅/❌
- [ ] Test 3d: Vault bearer auth → 200 ✅/❌
- [ ] Test 4: Error handling (no crashes) ✅/❌
- [ ] Test 5: Admin login security ✅/❌

**Overall Status:** ✅ PASS / ❌ FAIL

**Notes:** ________________
