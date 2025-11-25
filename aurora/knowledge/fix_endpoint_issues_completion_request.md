# Fix Endpoint Configuration - Completion Request

## Objective
Diagnose and fix endpoint configuration issues causing interface connection failures and 404 errors.

## Critical Problems

### 1. Main Interface Connection Lost
**Symptom**: "Server connection lost - attempting to reconnect"
**Possible Causes**:
- Backend (5000) not responding
- Frontend pointing to wrong backend URL
- CORS blocking requests
- Backend crashed or not fully started
- WebSocket connection failing

### 2. Chat Server 404 Error (Port 5003)
**Symptom**: "URL was not found" on port 5003
**Possible Causes**:
- Chat server routes not configured
- Wrong URL path being used
- Chat server not fully initialized
- Route handler missing

## Diagnostic Steps

### 1. Verify All Services Running
```bash
lsof -i -P -n | grep LISTEN | grep -E "5000|5001|5002|5003|5173"
ps aux | grep -E "node|python" | grep -v grep
```

### 2. Test Each Endpoint
```bash
curl -v http://localhost:5000/health
curl -v http://localhost:5000/healthz
curl -v http://localhost:5001/health
curl -v http://localhost:5002/health
curl -v http://localhost:5003/health
curl -v http://localhost:5003/chat
curl -v http://localhost:5003/api/chat
```

### 3. Check Service Logs
```bash
tmux capture-pane -t aurora-backend -p | tail -50
tmux capture-pane -t aurora-chat -p | tail -50
```

### 4. Check Frontend Configuration
- Look at client/src config files
- Verify API_URL or backend endpoint configuration
- Check for hardcoded URLs

### 5. Backend API Routes
- Verify server/index.ts has all routes configured
- Check for /api/* endpoints
- Verify health check routes exist

### 6. Chat Server Routes
- Check tools/luminar_nexus_v2.py chat server implementation
- Verify run_chat_server_v2() has proper routing
- Check if Flask/FastAPI routes are configured

## Fix Actions

### Fix Backend Connection
1. Check server/index.ts for CORS configuration
2. Verify backend is listening on 0.0.0.0 (not just localhost)
3. Check if health endpoints exist
4. Restart backend if needed

### Fix Chat Server (5003)
1. Find chat server implementation in luminar_nexus_v2.py
2. Add missing routes (/health, /chat, /api/chat)
3. Ensure proper route handlers exist
4. Restart chat server

### Fix Frontend Connection
1. Check client/.env or config for API_URL
2. Update to correct backend URL (http://localhost:5000)
3. Verify VITE_API_URL or similar variables
4. Rebuild frontend if needed

### Verify CORS
1. Backend must allow frontend origin (localhost:5173)
2. Add proper CORS headers
3. Allow credentials if using sessions/cookies

## Deliverables

1. **Diagnostic Report**: `.aurora_knowledge/ENDPOINT_DIAGNOSTIC_REPORT.md`
   - List of all endpoint statuses
   - Identified issues
   - Root causes

2. **Fixed Files**:
   - Update any incorrect endpoint configurations
   - Fix missing routes
   - Update CORS settings

3. **Verification**:
   - All 5 services respond to health checks
   - Chat server (5003) returns proper responses
   - Frontend can connect to backend
   - No more "connection lost" errors

## Success Criteria
- ✅ All services return 200 on health checks
- ✅ Port 5003 has working /health and /chat routes
- ✅ Frontend successfully connects to backend
- ✅ No 404 errors on any endpoint
- ✅ Main interface loads and works

## Aurora's Tools
- Tier 28: Autonomous Tool Use (read files, run commands, modify code)
- Tier 12: Networking & Protocols expertise
- autonomous_system.run_command() to test endpoints
- autonomous_system.read_file() to check configurations
- autonomous_system.modify_file() to fix issues

**CRITICAL: Interface is broken - needs immediate fix!**
