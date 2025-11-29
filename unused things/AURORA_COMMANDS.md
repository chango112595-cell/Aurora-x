# Aurora Terminal Commands Reference

**Last Updated:** November 28, 2025 | **Active Services:** Aurora V3 + Luminar Nexus V2

---

## Quick Start

```bash
# Both services are already running in workflows!
# Just use the commands below to interact with them.
```

---

## Chat & Conversations

### Send a Chat Message
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"your message here"}'
```

### Code Generation
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"write a sorting algorithm in python"}'
```

### Debugging Help
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"why is my function returning undefined"}'
```

### Get Explanations
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"explain how REST APIs work"}'
```

### Architecture Advice
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"how should i structure a microservices architecture"}'
```

### Build Components
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"build a react form component with validation"}'
```

---

## Status & Health Checks

### Check Aurora Status
```bash
curl http://localhost:5000/api/status
```

### Check Luminar Nexus V2 Status
```bash
curl http://localhost:8000/api/nexus/status
```

### Health Check
```bash
curl http://localhost:5000/api/health
```

### Pretty Print with jq
```bash
curl -s http://localhost:5000/api/status | jq
curl -s http://localhost:8000/api/nexus/status | jq
```

---

## Luminar Nexus V2 - ML Learning System

### View All Learned Patterns
```bash
curl http://localhost:8000/api/nexus/learned-conversation-patterns
```

### View Patterns for Specific Type
```bash
curl http://localhost:8000/api/nexus/learned-conversation-patterns/code_generation
```

### Analyze Keyword Correlations
```bash
curl http://localhost:8000/api/nexus/keyword-correlations/code_generation/debugging
```

### Pretty Print ML Data
```bash
curl -s http://localhost:8000/api/nexus/learned-conversation-patterns | jq
```

---

## Bridge Service

### Natural Language to Spec
```bash
curl -X POST http://localhost:5000/api/bridge/nl \
  -H "Content-Type: application/json" \
  -d '{"prompt":"create a user authentication system"}'
```

### Open Rollback for PR
```bash
curl -X POST http://localhost:5000/api/bridge/rollback/open \
  -H "Content-Type: application/json" \
  -d '{"pr_number":123,"reason":"feature not working"}'
```

### Rollback Merged Code
```bash
curl -X POST http://localhost:5000/api/bridge/rollback/merged \
  -H "Content-Type: application/json" \
  -d '{"commit_hash":"abc123","reason":"critical bug"}'
```

---

## Conversation Types Aurora Detects

Aurora automatically classifies conversations into:
- `code_generation` - Write code, functions, components
- `debugging` - Fix bugs, troubleshoot issues
- `explanation` - Learn concepts, understand code
- `architecture` - System design, planning
- `optimization` - Performance improvements
- `testing` - Test writing, QA strategies
- `refactoring` - Code reorganization
- `analysis` - Code analysis, patterns
- `question_answering` - Knowledge questions
- `general_chat` - Casual conversation

---

## Pretty Print Responses

### Format JSON Output
```bash
curl -s -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"build a react component"}' | jq
```

### Extract Just the Response
```bash
curl -s -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"write a function"}' | jq -r '.response'
```

### Save Response to File
```bash
curl -s -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"create a database schema"}' > response.json
```

---

## One-Liners for Quick Testing

```bash
# Test chat is working
curl -s http://localhost:5000/api/chat -X POST \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}' | jq '.type'

# Check both services alive
curl -s http://localhost:5000/api/status && echo "✓ V3" && \
curl -s http://localhost:8000/api/nexus/status && echo "✓ V2"

# View latest learned patterns
curl -s http://localhost:8000/api/nexus/learned-conversation-patterns | jq '.code_generation'

# Test code detection
curl -s http://localhost:5000/api/chat -X POST \
  -H "Content-Type: application/json" \
  -d '{"message":"write a hello world function"}' | jq '.type'
```

---

## Services Overview

| Service | Port | Status | Purpose |
|---------|------|--------|---------|
| Aurora V3 Backend | 5000 | Running | Express + Frontend, Chat API |
| Luminar Nexus V2 | 8000 | Running | ML Learning, Pattern Analysis |

---

## Quick Reference

**Browser Access:**
- Open: http://localhost:5000

**Test Aurora:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"hello"}'
```

**Test V2:**
```bash
curl http://localhost:8000/api/nexus/status | jq
```

**View ML Patterns:**
```bash
curl http://localhost:8000/api/nexus/learned-conversation-patterns | jq
```
