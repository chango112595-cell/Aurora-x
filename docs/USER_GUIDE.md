# Aurora-X User Guide

Welcome to Aurora-X, the comprehensive AI-powered platform for natural language processing, code synthesis, and intelligent problem solving!

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Quick Start](#quick-start)
3. [Core Features](#core-features)
4. [Natural Language Compilation](#natural-language-compilation)
5. [Intelligent Problem Solving](#intelligent-problem-solving)
6. [Chat Interface](#chat-interface)
7. [Monitoring & Performance](#monitoring--performance)
8. [Self-Learning System](#self-learning-system)
9. [Common Workflows](#common-workflows)
10. [Tips & Best Practices](#tips--best-practices)
11. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites

- **Docker** (recommended) or Python 3.10+
- **Redis** (optional, for production caching)
- **PostgreSQL** (optional, for persistent storage)
- Web browser for dashboard access

### Installation

#### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/chango112595-cell/Aurora-x.git
cd Aurora-x

# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps
```

#### Option 2: Local Development

```bash
# Clone the repository
git clone https://github.com/chango112595-cell/Aurora-x.git
cd Aurora-x

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python -m aurora_x.serve
```

### Accessing Aurora-X

Once started, Aurora-X is available at:

- **Main API:** http://localhost:5002
- **Interactive Docs:** http://localhost:5002/docs
- **Dashboard:** http://localhost:5002/dashboard/demos
- **Control Center:** http://localhost:5002/control
- **Health Check:** http://localhost:5002/healthz

---

## Quick Start

### Your First API Call

```bash
# Simple health check
curl http://localhost:5002/healthz

# Solve a math problem
curl -X POST http://localhost:5002/api/solve \
  -H "Content-Type: application/json" \
  -d '{"text": "What is 2 + 2?"}'

# Generate code from English
curl -X POST http://localhost:5002/api/nl/compile \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a function to calculate fibonacci numbers"}'
```

### Using the Interactive Dashboard

1. Open http://localhost:5002/docs in your browser
2. Explore available endpoints in the Swagger UI
3. Click "Try it out" on any endpoint
4. Fill in parameters and click "Execute"
5. View the response below

---

## Core Features

### 🤖 Natural Language Compilation

Convert English descriptions into working code:

**What it does:**
- Parses natural language prompts
- Generates complete Python functions
- Creates test cases automatically
- Produces documentation
- Supports Flask web apps

**Best for:**
- Rapid prototyping
- Learning new concepts
- Generating boilerplate code
- Creating microservices

---

### 🧮 Intelligent Problem Solving

Solve problems across multiple domains:

**Supported Domains:**
- **Mathematics:** Algebra, calculus, statistics
- **Physics:** Mechanics, thermodynamics, electromagnetism
- **Chemistry:** Stoichiometry, molecular calculations
- **Logic:** Boolean algebra, propositional logic
- **Units:** Conversions between measurement systems

**Best for:**
- Homework assistance
- Engineering calculations
- Scientific computing
- Unit conversions
- Quick math checks

---

### 💬 Conversational AI

Natural language chat interface:

**Capabilities:**
- Context-aware conversations
- Multi-turn dialogues
- Intent recognition
- Task delegation
- Knowledge retrieval

**Best for:**
- Asking questions
- Getting explanations
- Exploring topics
- Step-by-step guidance

---

### 📊 Monitoring & Performance

Real-time system monitoring:

**Features:**
- Health checks
- Performance metrics
- Cache statistics
- Request profiling
- Slow query detection

**Best for:**
- Production monitoring
- Performance optimization
- Debugging issues
- Capacity planning

---

## Natural Language Compilation

### Basic Usage

```bash
curl -X POST http://localhost:5002/api/nl/compile \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a function to sort a list using quicksort"
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
  "message": "Code generated successfully"
}
```

### Example Prompts

#### 1. Simple Function
```
"Write a function that checks if a number is prime"
```

**Generates:**
- `is_prime.py`: Implementation with docstring
- `test_is_prime.py`: Unit tests
- `README.md`: Usage documentation

#### 2. Flask Application
```
"Create a Flask API with endpoints for user CRUD operations"
```

**Generates:**
- `app.py`: Flask application
- `models.py`: User model
- `routes.py`: API endpoints
- `requirements.txt`: Dependencies
- `test_app.py`: API tests

#### 3. Data Processing
```
"Build a function that reads a CSV file and calculates average by category"
```

**Generates:**
- `csv_processor.py`: CSV parsing and aggregation
- `test_csv_processor.py`: Tests with sample data
- `sample_data.csv`: Example dataset

### Advanced Features

#### Specify Requirements

```
"Create a Flask API for user authentication with JWT tokens, 
password hashing using bcrypt, and email validation"
```

#### Multiple Functions

```
"Write functions for: 
1. Binary search in a sorted array
2. Merge two sorted arrays
3. Find the kth largest element"
```

#### Custom Framework

```
"Build a FastAPI service with async endpoints for weather data,
using httpx for external API calls and caching responses for 5 minutes"
```

### Viewing Generated Code

```bash
# List all runs
ls -la runs/

# View the latest generated code
cd runs/latest
cat *.py

# Run generated tests
python -m pytest test_*.py
```

---

## Intelligent Problem Solving

### Mathematics

#### Algebra
```bash
curl -X POST http://localhost:5002/api/solve \
  -H "Content-Type: application/json" \
  -d '{"text": "Solve for x: 2x + 5 = 15"}'
```

**Response:**
```json
{
  "ok": true,
  "domain": "mathematics",
  "task": "linear_equation",
  "result": {"x": 5.0},
  "explanation": "Subtract 5 from both sides: 2x = 10. Divide by 2: x = 5"
}
```

#### Calculus
```bash
curl -X POST http://localhost:5002/api/solve \
  -H "Content-Type: application/json" \
  -d '{"text": "What is the derivative of x^3 + 2x^2 - 5x + 1?"}'
```

**Response:**
```json
{
  "ok": true,
  "domain": "mathematics",
  "task": "differentiation",
  "input": "x^3 + 2x^2 - 5x + 1",
  "result": "3x^2 + 4x - 5",
  "explanation": "Apply power rule to each term"
}
```

#### Statistics
```bash
curl -X POST http://localhost:5002/api/solve \
  -H "Content-Type: application/json" \
  -d '{"text": "Calculate mean, median, and standard deviation of: 5, 10, 15, 20, 25"}'
```

### Physics

#### Mechanics
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
    "acceleration": 5
  },
  "result": {
    "force": 50.0,
    "unit": "N"
  },
  "explanation": "Using F = ma: 10 kg × 5 m/s² = 50 N"
}
```

#### Energy
```bash
curl -X POST http://localhost:5002/api/solve \
  -H "Content-Type: application/json" \
  -d '{"text": "What is the kinetic energy of a 5kg object moving at 10m/s?"}'
```

### Chemistry

```bash
curl -X POST http://localhost:5002/api/solve \
  -H "Content-Type: application/json" \
  -d '{"text": "Balance the equation: H2 + O2 -> H2O"}'
```

**Response:**
```json
{
  "ok": true,
  "domain": "chemistry",
  "task": "equation_balancing",
  "result": "2H2 + O2 -> 2H2O",
  "explanation": "2 hydrogen molecules + 1 oxygen molecule -> 2 water molecules"
}
```

### Unit Conversions

```bash
# Temperature
curl -X POST http://localhost:5002/api/solve \
  -H "Content-Type: application/json" \
  -d '{"text": "Convert 100 fahrenheit to celsius"}'

# Length
curl -X POST http://localhost:5002/api/solve \
  -H "Content-Type: application/json" \
  -d '{"text": "How many meters in 5 kilometers?"}'

# Volume
curl -X POST http://localhost:5002/api/solve \
  -H "Content-Type: application/json" \
  -d '{"text": "Convert 2 gallons to liters"}'
```

### Pretty Output

For human-readable results, use the `/api/solve/pretty` endpoint:

```bash
curl -X POST http://localhost:5002/api/solve/pretty \
  -H "Content-Type: application/json" \
  -d '{"text": "Calculate the area of a circle with radius 5"}'
```

**Response:**
```
==================================================
Domain: mathematics
Task: circle_area
--------------------------------------------------
Input: radius = 5
Result:
  area: 78.539816

Explanation: Using the formula A = πr², where r = 5:
A = π × 5² = π × 25 ≈ 78.54 square units
==================================================
```

---

## Chat Interface

### Starting a Conversation

```bash
curl -X POST http://localhost:5002/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! Can you explain what Aurora-X does?",
    "context_id": "session-1"
  }'
```

**Response:**
```json
{
  "response": "Aurora-X is an AI-powered platform that combines natural language processing, code generation, and intelligent problem solving. I can help you generate code from English descriptions, solve math and physics problems, answer questions, and more!",
  "context_id": "session-1",
  "intent": "greeting_and_question",
  "confidence": 0.98
}
```

### Multi-Turn Conversations

```bash
# First message
curl -X POST http://localhost:5002/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need to sort a list of numbers",
    "context_id": "coding-session"
  }'

# Follow-up (uses same context_id)
curl -X POST http://localhost:5002/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you make it work in-place?",
    "context_id": "coding-session"
  }'
```

### Ask for Explanations

```bash
curl -X POST http://localhost:5002/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain how quicksort works",
    "context_id": "learning"
  }'
```

---

## Monitoring & Performance

### Check System Health

```bash
# Basic health check
curl http://localhost:5002/healthz

# Detailed health check
curl http://localhost:5002/api/self-monitor/health
```

### View Performance Metrics

```bash
# Overall statistics
curl http://localhost:5002/api/performance/stats

# Cache statistics
curl http://localhost:5002/api/performance/cache/stats

# Slow requests
curl http://localhost:5002/api/performance/slow-requests
```

### Cache Management

```bash
# Clear all cache
curl -X POST "http://localhost:5002/api/performance/cache/clear?pattern=*"

# Clear specific cache prefix
curl -X POST "http://localhost:5002/api/performance/cache/clear?pattern=solver:*"
```

### Progress Tracking

```bash
# View current progress
curl http://localhost:5002/api/progress

# Get progress badge
curl http://localhost:5002/badge/progress.svg > progress.svg
```

---

## Self-Learning System

### What is Self-Learning?

Aurora-X includes an autonomous learning system that:
- Analyzes past solutions and errors
- Discovers optimization opportunities
- Tests improvements automatically
- Learns from user interactions

### Managing Self-Learning

```bash
# Check status
curl http://localhost:5002/api/self-learning/status

# Start the daemon
curl -X POST http://localhost:5002/api/self-learning/start

# Stop the daemon
curl -X POST http://localhost:5002/api/self-learning/stop
```

### When to Use Self-Learning

**Enable when:**
- Running in development
- Testing new features
- Want automatic improvements
- Have spare CPU cycles

**Disable when:**
- Running in production
- Need consistent behavior
- Limited resources
- During critical operations

---

## Common Workflows

### Workflow 1: Generate and Deploy Code

```bash
# 1. Generate code
curl -X POST http://localhost:5002/api/nl/compile \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a Flask API for todo list"}' \
  > response.json

# 2. Extract run_id
RUN_ID=$(jq -r '.run_id' response.json)

# 3. Review generated code
cd runs/$RUN_ID
cat app.py

# 4. Run tests
python -m pytest

# 5. Start the Flask app
python app.py
```

### Workflow 2: Solve and Explain

```bash
# 1. Solve the problem
curl -X POST http://localhost:5002/api/solve \
  -H "Content-Type: application/json" \
  -d '{"text": "Integrate x^2 from 0 to 5"}' \
  > solution.json

# 2. Get explanation via chat
curl -X POST http://localhost:5002/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you explain how to integrate x^2?",
    "context_id": "math-help"
  }'
```

### Workflow 3: Monitor Performance

```bash
# 1. Check baseline performance
curl http://localhost:5002/api/performance/stats > baseline.json

# 2. Run your workload
# ... your API calls ...

# 3. Check performance again
curl http://localhost:5002/api/performance/stats > after.json

# 4. Compare results
diff baseline.json after.json

# 5. Check for slow requests
curl http://localhost:5002/api/performance/slow-requests
```

### Workflow 4: Debugging Issues

```bash
# 1. Check system health
curl http://localhost:5002/api/self-monitor/health

# 2. Try auto-healing
curl -X POST http://localhost:5002/api/self-monitor/auto-heal

# 3. Clear cache if needed
curl -X POST "http://localhost:5002/api/performance/cache/clear?pattern=*"

# 4. Restart services
docker-compose restart
```

---

## Tips & Best Practices

### Natural Language Compilation

✅ **DO:**
- Be specific about requirements
- Mention frameworks/libraries you want
- Specify input/output formats
- Include edge cases to handle

❌ **DON'T:**
- Use vague descriptions
- Mix multiple unrelated features
- Forget to specify error handling
- Omit type information

**Good Example:**
```
"Create a Flask REST API with GET and POST endpoints for user management.
Use SQLAlchemy for database, validate email format, hash passwords with bcrypt,
and return JSON responses with proper HTTP status codes."
```

**Bad Example:**
```
"Make a user API"
```

### Problem Solving

✅ **DO:**
- Include units in physics problems
- Specify precision for calculations
- Provide all necessary values
- State what you want to find

❌ **DON'T:**
- Omit units
- Use ambiguous variable names
- Forget to mention constraints
- Mix multiple questions

**Good Example:**
```
"Calculate the final velocity of a 5kg object that starts from rest and 
accelerates at 3m/s² for 10 seconds. Give answer in m/s."
```

**Bad Example:**
```
"How fast is it going?"
```

### Performance Optimization

✅ **DO:**
- Enable caching for repeated queries
- Use cache prefixes to organize
- Clear cache after updates
- Monitor slow requests

❌ **DON'T:**
- Cache everything blindly
- Use very long TTLs for dynamic data
- Forget to invalidate stale cache
- Ignore performance metrics

### Monitoring

✅ **DO:**
- Check health regularly
- Set up alerting for production
- Review slow requests weekly
- Track cache hit rates

❌ **DON'T:**
- Ignore warning signals
- Disable monitoring in production
- Let cache grow unbounded
- Overlook memory usage

---

## Troubleshooting

### Issue: Service Won't Start

**Symptoms:**
- Connection refused errors
- Port already in use

**Solutions:**
```bash
# Check if port is in use
lsof -i :5002

# Kill the process using the port
kill -9 <PID>

# Or use a different port
AURORA_PORT=5003 python -m aurora_x.serve
```

### Issue: Slow Response Times

**Symptoms:**
- Requests taking >5 seconds
- High CPU usage

**Solutions:**
```bash
# Check slow requests
curl http://localhost:5002/api/performance/slow-requests

# Enable caching
# (Caching is enabled by default)

# Clear old cache
curl -X POST "http://localhost:5002/api/performance/cache/clear?pattern=*"

# Restart services
docker-compose restart
```

### Issue: Out of Memory

**Symptoms:**
- Service crashes
- OOMKilled in Docker logs

**Solutions:**
```bash
# Increase Docker memory limit
# Edit docker-compose.yml:
#   mem_limit: 2g  # Increase from 1g

# Clear cache
curl -X POST "http://localhost:5002/api/performance/cache/clear?pattern=*"

# Reduce cache size
# Edit aurora_x/cache.py:
#   max_memory_items=500  # Reduce from 1000
```

### Issue: Code Generation Fails

**Symptoms:**
- Status: "error" in response
- No files generated

**Solutions:**
```bash
# Check the error message
curl -X POST http://localhost:5002/api/nl/compile \
  -H "Content-Type: application/json" \
  -d '{"prompt": "..."}' | jq '.message'

# Try a simpler prompt
curl -X POST http://localhost:5002/api/nl/compile \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a function to add two numbers"}'

# Check logs
docker-compose logs aurora-backend
```

### Issue: Solver Gives Wrong Answer

**Symptoms:**
- Incorrect results
- Missing units

**Solutions:**
```bash
# Be more specific with units
curl -X POST http://localhost:5002/api/solve \
  -H "Content-Type: application/json" \
  -d '{"text": "Convert 100 degrees fahrenheit to celsius"}'

# Use pretty output for clarity
curl -X POST http://localhost:5002/api/solve/pretty \
  -H "Content-Type: application/json" \
  -d '{"text": "..."}'

# Check if domain is correct in response
# If wrong domain detected, rephrase the question
```

### Issue: Cache Not Working

**Symptoms:**
- Cache hit rate is 0%
- Responses still slow

**Solutions:**
```bash
# Check cache status
curl http://localhost:5002/api/performance/cache/stats

# Verify Redis is running (production)
docker-compose ps redis

# Check cache warnings in logs
docker-compose logs aurora-backend | grep cache

# For development, memory cache should work automatically
```

### Getting Help

If you're still stuck:

1. Check the logs:
   ```bash
   docker-compose logs aurora-backend
   ```

2. Visit the interactive docs:
   ```
   http://localhost:5002/docs
   ```

3. Check GitHub issues:
   ```
   https://github.com/chango112595-cell/Aurora-x/issues
   ```

4. Enable debug mode:
   ```bash
   export DEBUG=true
   python -m aurora_x.serve
   ```

---

## Next Steps

- Read the [API Reference](API_REFERENCE.md) for detailed endpoint documentation
- See [Developer Guide](DEVELOPER_GUIDE.md) for contributing
- Check [Deployment Guide](DEPLOYMENT_GUIDE.md) for production setup
- Review [Performance Guide](PERFORMANCE_GUIDE.md) for optimization

---

**Happy coding with Aurora-X!** 🚀

*Last Updated: November 10, 2025*
