# Aurora-X API Reference

**Version:** 3.0.0  
**Base URL:** `http://localhost:5002`  
**API Documentation:** `http://localhost:5002/docs` (Swagger UI)  
**Alternative Docs:** `http://localhost:5002/redoc` (ReDoc)

---

## Table of Contents

1. [Authentication](#authentication)
2. [Health & Monitoring](#health--monitoring)
3. [Natural Language Compilation](#natural-language-compilation)
4. [Intelligent Solver](#intelligent-solver)
5. [Chat Interface](#chat-interface)
6. [Performance & Caching](#performance--caching)
7. [Self-Learning System](#self-learning-system)
8. [Progress Tracking](#progress-tracking)
9. [Bridge API](#bridge-api)
10. [Response Codes](#response-codes)
11. [Rate Limiting](#rate-limiting)

---

## Authentication

Currently, most endpoints are open for development. Production deployments should enable authentication:

```bash
# Future authentication (when enabled)
curl -X POST http://localhost:5002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

Use the token in subsequent requests:
```bash
curl http://localhost:5002/api/endpoint \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1..."
```

---

## Health & Monitoring

### GET /healthz

Basic health check endpoint.

**Tags:** `health`

```bash
curl http://localhost:5002/healthz
```

**Response:**
```json
{
  "ok": true,
  "t08_enabled": true,
  "ts": 1699632000.123
}
```

**Fields:**
- `ok` (boolean): Service is running
- `t08_enabled` (boolean): Intent router enabled
- `ts` (float): Unix timestamp

---

### GET /api/self-monitor/health

Comprehensive health check with service diagnostics.

**Tags:** `monitoring`

```bash
curl http://localhost:5002/api/self-monitor/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-10T20:30:00",
  "services_checked": {
    "solver": "healthy",
    "chat_interface": "healthy",
    "file_system": "healthy"
  },
  "self_healing": "active"
}
```

**Status Values:**
- `healthy`: All systems operational
- `degraded`: Some services experiencing issues
- `error`: Critical failure detected

---

### POST /api/self-monitor/auto-heal

Trigger self-healing and recovery processes.

**Tags:** `monitoring`

```bash
curl -X POST http://localhost:5002/api/self-monitor/auto-heal
```

**Response:**
```json
{
  "status": "healing_complete",
  "timestamp": "2025-11-10T20:30:00",
  "actions_taken": [
    "cleared_internal_cache",
    "verified_solver_functionality"
  ],
  "recommendation": "Service should now be fully functional"
}
```

---

## Natural Language Compilation

### POST /api/nl/compile

Convert natural language descriptions into working code.

**Tags:** `compilation`

**Request Body:**
```json
{
  "prompt": "Create a Flask API that calculates fibonacci numbers"
}
```

**Example:**
```bash
curl -X POST http://localhost:5002/api/nl/compile \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a function that sorts a list of numbers using quicksort"
  }'
```

**Response:**
```json
{
  "run_id": "run-20251110-203000",
  "status": "success",
  "files_generated": [
    "runs/run-20251110-203000/quicksort.py",
    "runs/run-20251110-203000/test_quicksort.py"
  ],
  "message": "Code generated successfully from natural language prompt"
}
```

**Supported Frameworks:**
- Flask web applications
- Python functions with specs
- General-purpose scripts

**Example Prompts:**
- "Create a Flask API that calculates fibonacci numbers"
- "Write a function that sorts a list of numbers"
- "Build a REST endpoint for user authentication"
- "Generate a function to parse CSV files"

---

## Intelligent Solver

### POST /api/solve

Solve problems across multiple domains with structured JSON output.

**Tags:** `solver`

**Request Body:**
```json
{
  "text": "What is the derivative of x^2 + 3x - 5?"
}
```

**Example:**
```bash
curl -X POST http://localhost:5002/api/solve \
  -H "Content-Type: application/json" \
  -d '{"text": "Calculate the force on a 10kg object accelerating at 5m/s^2"}'
```

**Response:**
```json
{
  "ok": true,
  "domain": "physics",
  "task": "force_calculation",
  "input": {
    "mass": 10,
    "acceleration": 5,
    "unit": "N"
  },
  "result": {
    "force": 50.0,
    "unit": "N"
  },
  "explanation": "Using Newton's second law (F = ma), force = 10 kg × 5 m/s² = 50 N"
}
```

**Supported Domains:**
- **Mathematics**: Algebra, calculus, statistics, linear algebra
- **Physics**: Mechanics, thermodynamics, electromagnetism
- **Chemistry**: Stoichiometry, molecular calculations
- **Logic**: Boolean algebra, propositional logic
- **Units**: SI units, imperial conversions

**Example Problems:**
```bash
# Mathematics
curl -X POST http://localhost:5002/api/solve \
  -H "Content-Type: application/json" \
  -d '{"text": "Integrate x^2 from 0 to 5"}'

# Physics
curl -X POST http://localhost:5002/api/solve \
  -H "Content-Type: application/json" \
  -d '{"text": "Calculate kinetic energy of 5kg mass at 10m/s"}'

# Chemistry
curl -X POST http://localhost:5002/api/solve \
  -H "Content-Type: application/json" \
  -d '{"text": "Balance equation: H2 + O2 -> H2O"}'

# Unit Conversion
curl -X POST http://localhost:5002/api/solve \
  -H "Content-Type: application/json" \
  -d '{"text": "Convert 100 fahrenheit to celsius"}'
```

---

### POST /api/solve/pretty

Solve problems with human-readable formatted output.

**Tags:** `solver`

**Request Body:**
```json
{
  "text": "Solve the quadratic equation: x^2 - 5x + 6 = 0"
}
```

**Example:**
```bash
curl -X POST http://localhost:5002/api/solve/pretty \
  -H "Content-Type: application/json" \
  -d '{"text": "Find the roots of x^2 - 5x + 6 = 0"}'
```

**Response (Plain Text):**
```
==================================================
Domain: mathematics
Task: quadratic_equation
--------------------------------------------------
Input: x^2 - 5x + 6 = 0
Result:
  x1: 2.000000
  x2: 3.000000

Explanation: Using the quadratic formula, the roots are x = 2 and x = 3
==================================================
```

---

## Chat Interface

### POST /api/chat

Conversational AI interface with context awareness.

**Tags:** `chat`

**Request Body:**
```json
{
  "message": "Hello, can you help me solve a physics problem?",
  "context_id": "optional-session-id"
}
```

**Example:**
```bash
curl -X POST http://localhost:5002/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the speed of light?",
    "context_id": "physics-session-1"
  }'
```

**Response:**
```json
{
  "response": "The speed of light in vacuum is approximately 299,792,458 meters per second (often rounded to 3.0 × 10^8 m/s).",
  "context_id": "physics-session-1",
  "intent": "question_answering",
  "confidence": 0.98
}
```

---

## Performance & Caching

### GET /api/performance/stats

Get overall performance and cache statistics.

**Tags:** `performance`

```bash
curl http://localhost:5002/api/performance/stats
```

**Response:**
```json
{
  "cache": {
    "type": "redis",
    "total_keys": 1247,
    "hit_rate": 0.87,
    "hits": 5432,
    "misses": 812
  },
  "requests": {
    "total": 15234,
    "average_time": 0.042,
    "slow_count": 23
  }
}
```

---

### GET /api/performance/cache/stats

Get detailed cache statistics.

**Tags:** `performance`

```bash
curl http://localhost:5002/api/performance/cache/stats
```

**Response:**
```json
{
  "type": "redis",
  "total_keys": 1247,
  "max_size": 10000,
  "ttl": 300,
  "hit_rate": 0.87,
  "hits": 5432,
  "misses": 812,
  "evictions": 45
}
```

---

### POST /api/performance/cache/clear

Clear cache by pattern.

**Tags:** `performance`

**Query Parameters:**
- `pattern` (string): Pattern to match keys (supports wildcards `*`)

```bash
# Clear all cache
curl -X POST "http://localhost:5002/api/performance/cache/clear?pattern=*"

# Clear user-related cache
curl -X POST "http://localhost:5002/api/performance/cache/clear?pattern=user:*"

# Clear specific cache prefix
curl -X POST "http://localhost:5002/api/performance/cache/clear?pattern=solver:*"
```

**Response:**
```json
{
  "cleared": true,
  "pattern": "user:*",
  "keys_cleared": 127
}
```

---

### GET /api/performance/slow-requests

Get recent slow requests (>1s response time).

**Tags:** `performance`

```bash
curl http://localhost:5002/api/performance/slow-requests
```

**Response:**
```json
{
  "slow_requests": [
    {
      "method": "POST",
      "path": "/api/solve",
      "duration": 2.34,
      "timestamp": "2025-11-10T20:30:00"
    },
    {
      "method": "POST",
      "path": "/api/nl/compile",
      "duration": 5.67,
      "timestamp": "2025-11-10T20:29:45"
    }
  ],
  "threshold": 1.0,
  "count": 23
}
```

---

### GET /api/performance/metrics

Get condensed performance metrics for monitoring.

**Tags:** `performance`

```bash
curl http://localhost:5002/api/performance/metrics
```

**Response:**
```json
{
  "requests_total": 15234,
  "requests_per_second": 5.2,
  "average_response_time": 0.042,
  "cache_hit_rate": 0.87,
  "slow_requests_count": 23
}
```

---

## Self-Learning System

### GET /api/self-learning/status

Check if the autonomous self-learning daemon is running.

**Tags:** `self-learning`

```bash
curl http://localhost:5002/api/self-learning/status
```

**Response:**
```json
{
  "running": true,
  "pid": 12345,
  "daemon_active": true,
  "last_check": 1699632000.123
}
```

---

### POST /api/self-learning/start

Start the autonomous self-learning daemon.

**Tags:** `self-learning`

```bash
curl -X POST http://localhost:5002/api/self-learning/start
```

**Response:**
```json
{
  "status": "started",
  "pid": 12345
}
```

**Configuration:**
- Sleep interval: 15 seconds
- Max iterations: 50 per session
- Beam width: 20

---

### POST /api/self-learning/stop

Stop the self-learning daemon.

**Tags:** `self-learning`

```bash
curl -X POST http://localhost:5002/api/self-learning/stop
```

**Response:**
```json
{
  "status": "stopped",
  "stopped_pids": [12345]
}
```

---

## Progress Tracking

### GET /api/progress

Get current task progress.

**Tags:** `progress`

```bash
curl http://localhost:5002/api/progress
```

**Response:**
```json
{
  "tasks": [
    {
      "name": "Docker containerization",
      "status": "complete",
      "percent": 100
    },
    {
      "name": "Performance optimization",
      "status": "in_progress",
      "percent": 75
    }
  ],
  "overall_progress": 87
}
```

---

### POST /api/progress/ui_thresholds

Update UI progress thresholds.

**Tags:** `progress`

**Request Body:**
```json
{
  "ui_thresholds": {
    "ok": 80,
    "warn": 50
  }
}
```

```bash
curl -X POST http://localhost:5002/api/progress/ui_thresholds \
  -H "Content-Type: application/json" \
  -d '{"ui_thresholds": {"ok": 80, "warn": 50}}'
```

**Response:**
```json
{
  "status": "updated",
  "ui_thresholds": {
    "ok": 80,
    "warn": 50
  }
}
```

---

### GET /badge/progress.svg

Get dynamic SVG progress badge.

**Tags:** `progress`

```bash
curl http://localhost:5002/badge/progress.svg
```

Returns an SVG image showing current progress percentage with color coding:
- Green (≥80%): All systems go
- Blue (≥50%): Good progress
- Red (<50%): Needs attention

**Usage in Markdown:**
```markdown
![Progress](http://localhost:5002/badge/progress.svg)
```

---

## Bridge API

### POST /api/bridge/nl

Convert natural language to spec.

**Tags:** `bridge`

```bash
curl -X POST http://localhost:5002/api/bridge/nl \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a function to calculate fibonacci"}'
```

---

### POST /api/bridge/spec

Compile spec to code.

**Tags:** `bridge`

```bash
curl -X POST http://localhost:5002/api/bridge/spec \
  -H "Content-Type: application/json" \
  -d @spec.json
```

---

### POST /api/bridge/deploy

Deploy compiled code.

**Tags:** `bridge`

```bash
curl -X POST http://localhost:5002/api/bridge/deploy \
  -H "Content-Type: application/json" \
  -d '{"run_id": "run-20251110-203000"}'
```

---

## Response Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error occurred |
| 503 | Service Unavailable | Service temporarily unavailable |

---

## Rate Limiting

**Current Status:** No rate limiting in development mode.

**Production Configuration:**
- Default: 100 requests per minute per IP
- Authenticated users: 1000 requests per minute
- Heavy endpoints (compilation, solving): 10 requests per minute

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699632060
```

**Exceeded Response:**
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 45
}
```

---

## Error Handling

All errors follow this structure:

```json
{
  "error": "Description of what went wrong",
  "error_code": "SPECIFIC_ERROR_CODE",
  "details": {
    "field": "Additional context"
  },
  "timestamp": "2025-11-10T20:30:00"
}
```

**Common Error Codes:**
- `INVALID_INPUT`: Request data validation failed
- `COMPILATION_FAILED`: Code generation error
- `SOLVER_ERROR`: Problem solving failed
- `CACHE_ERROR`: Cache operation failed
- `SERVICE_UNAVAILABLE`: Required service is down

---

## Pagination

For list endpoints that return many results:

**Request:**
```bash
curl "http://localhost:5002/api/endpoint?page=2&per_page=50"
```

**Response:**
```json
{
  "items": [...],
  "pagination": {
    "page": 2,
    "per_page": 50,
    "total_items": 500,
    "total_pages": 10,
    "has_next": true,
    "has_prev": true
  }
}
```

---

## WebSocket Endpoints

### WS /ws/spec_updates

Real-time spec compilation updates.

```javascript
const ws = new WebSocket('ws://localhost:5002/ws/spec_updates');
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Compilation update:', update);
};
```

**Message Format:**
```json
{
  "run_id": "run-20251110-203000",
  "status": "compiling",
  "progress": 45,
  "message": "Generating test cases..."
}
```

---

## Interactive API Documentation

Aurora-X provides two interactive API documentation interfaces:

### Swagger UI (Recommended)
**URL:** `http://localhost:5002/docs`

Features:
- Try out API calls directly from the browser
- See request/response examples
- Download OpenAPI specification
- Test authentication flows

### ReDoc
**URL:** `http://localhost:5002/redoc`

Features:
- Clean, three-panel design
- Search across all endpoints
- Code samples in multiple languages
- Printable documentation

---

## SDKs and Client Libraries

**Python Client:**
```python
from aurora_x_client import AuroraClient

client = AuroraClient(base_url="http://localhost:5002")

# Solve a problem
result = client.solve("What is 2 + 2?")
print(result)

# Compile from natural language
code = client.compile("Create a Flask API for user auth")
print(code.files_generated)
```

**JavaScript/TypeScript Client:**
```typescript
import { AuroraClient } from '@aurora-x/client';

const client = new AuroraClient({ baseUrl: 'http://localhost:5002' });

// Solve a problem
const result = await client.solve('Calculate force from mass and acceleration');
console.log(result);
```

---

## Support

- **Documentation:** `/docs` (this file)
- **Interactive API:** `/docs` (Swagger UI)
- **GitHub:** https://github.com/chango112595-cell/Aurora-x
- **Issues:** https://github.com/chango112595-cell/Aurora-x/issues

---

**Last Updated:** November 10, 2025  
**API Version:** 3.0.0  
**Documentation Version:** 1.0.0
