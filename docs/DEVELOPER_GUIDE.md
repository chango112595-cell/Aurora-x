# Aurora-X Developer Guide

Welcome to the Aurora-X developer documentation! This guide will help you understand the architecture, contribute code, and extend Aurora-X.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Development Setup](#development-setup)
4. [Code Style Guidelines](#code-style-guidelines)
5. [Testing](#testing)
6. [Contributing](#contributing)
7. [Module Documentation](#module-documentation)
8. [Extending Aurora-X](#extending-aurora-x)
9. [Debugging](#debugging)
10. [Release Process](#release-process)

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  (Web Browser, CLI, API Clients, Mobile Apps)               │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                     API Gateway Layer                        │
│            FastAPI (serve.py) - Port 5002                   │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │ Health   │Compiler  │ Solver   │ Chat     │Performance│  │
│  │ Endpoints│API       │ API      │Interface │ API       │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                    Business Logic Layer                      │
│  ┌────────────────┬───────────────┬────────────────────┐   │
│  │ NL Compiler    │ Solver Engine │ Chat Engine        │   │
│  │ (spec parsing) │ (multi-domain)│ (conversation)     │   │
│  └────────────────┴───────────────┴────────────────────┘   │
│  ┌────────────────┬───────────────┬────────────────────┐   │
│  │ Self-Learning  │ Task Manager  │ Bridge Factory     │   │
│  │ (autonomous)   │ (progress)    │ (spec compilation) │   │
│  └────────────────┴───────────────┴────────────────────┘   │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                    Infrastructure Layer                      │
│  ┌────────────┬──────────┬────────────┬──────────────────┐ │
│  │ Redis      │PostgreSQL│ Prometheus │ File System      │ │
│  │ (cache)    │(database)│ (metrics)  │ (code storage)   │ │
│  └────────────┴──────────┴────────────┴──────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

1. **FastAPI Application (`aurora_x/serve.py`)**
   - Central HTTP server
   - Route registration
   - Middleware chain
   - Error handling

2. **Natural Language Compiler**
   - `spec/parser_nl.py`: English to spec
   - `tools/spec_from_text.py`: Spec generation
   - `tools/spec_compile_v3.py`: Code synthesis

3. **Solver Engine (`generators/solver.py`)**
   - Domain detection
   - Task routing
   - Multi-domain solving
   - Result formatting

4. **Chat System**
   - Intent recognition
   - Context management
   - Response generation
   - Conversation history

5. **Monitoring System**
   - Prometheus metrics
   - Health checks
   - Performance tracking
   - Alert management

6. **Caching Layer (`cache.py`)**
   - Redis integration
   - Memory fallback
   - TTL management
   - Pattern invalidation

---

## Project Structure

```
Aurora-x/
├── aurora_x/                    # Main application code
│   ├── serve.py                # FastAPI application entry point
│   ├── cache.py                # Caching infrastructure
│   ├── performance.py          # Performance middleware
│   ├── models.py               # Database models
│   ├── app_settings.py         # Configuration
│   ├── api/                    # API endpoints
│   │   ├── health_check.py    # Health endpoints
│   │   ├── monitoring.py      # Monitoring endpoints
│   │   ├── performance.py     # Performance endpoints
│   │   ├── commands.py         # Command endpoints
│   │   └── server_control.py  # Server control
│   ├── bridge/                 # Factory bridge
│   │   └── attach_bridge.py   # Bridge endpoints
│   ├── chat/                   # Chat system
│   │   ├── conversation.py    # Conversation engine
│   │   ├── attach_router_lang.py  # Intent router
│   │   └── ...                # Other chat modules
│   ├── generators/             # Code generation
│   │   └── solver.py          # Solver engine
│   ├── spec/                   # Spec processing
│   │   └── parser_nl.py       # NL parser
│   └── static/                 # Static files
│       └── templates/          # HTML templates
├── tools/                       # Utility scripts
│   ├── spec_from_text.py       # Spec generator
│   ├── spec_compile_v3.py      # Spec compiler
│   └── luminar_nexus.py        # Service orchestrator
├── alembic/                     # Database migrations
│   ├── versions/               # Migration scripts
│   └── env.py                  # Alembic config
├── tests/                       # Test suite
│   ├── test_api.py            # API tests
│   ├── test_solver.py         # Solver tests
│   └── ...                     # Other tests
├── docs/                        # Documentation
│   ├── API_REFERENCE.md       # API docs
│   ├── USER_GUIDE.md          # User documentation
│   ├── DEVELOPER_GUIDE.md     # This file
│   ├── DEPLOYMENT_GUIDE.md    # Deployment docs
│   └── PERFORMANCE_GUIDE.md   # Performance docs
├── examples/                    # Example code
│   └── cache_example.py        # Cache usage examples
├── scripts/                     # Deployment scripts
│   └── generate-nginx-config.sh  # Nginx config generator
├── docker-compose.yml           # Docker orchestration
├── Dockerfile                   # Container definition
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
└── README.md                    # Project overview
```

---

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- Docker & Docker Compose (optional)
- Redis (optional, for caching)
- PostgreSQL (optional, for database)

### Local Development Environment

```bash
# 1. Clone the repository
git clone https://github.com/chango112595-cell/Aurora-x.git
cd Aurora-x

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Install pre-commit hooks
pre-commit install

# 5. Set up environment variables
cp .env.example .env
# Edit .env with your settings

# 6. Initialize database
alembic upgrade head

# 7. Run tests to verify setup
pytest

# 8. Start the development server
python -m aurora_x.serve
```

### Development with Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f aurora-backend

# Run tests in container
docker-compose exec aurora-backend pytest

# Rebuild after code changes
docker-compose up -d --build

# Stop all services
docker-compose down
```

### IDE Setup

#### VS Code

Recommended extensions:
- Python
- Pylance
- Black Formatter
- autoDocstring
- GitLens

`.vscode/settings.json`:
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "editor.formatOnSave": true,
  "python.analysis.typeCheckingMode": "basic"
}
```

#### PyCharm

1. Open project
2. Set Python interpreter to `venv/bin/python`
3. Enable pytest as test runner
4. Configure Black as formatter
5. Enable type checking

---

## Code Style Guidelines

### Python Style

Follow PEP 8 with these specifics:

```python
# Good: Clear, typed, documented
def calculate_force(mass: float, acceleration: float) -> float:
    """
    Calculate force using Newton's second law.
    
    Args:
        mass: Mass in kilograms
        acceleration: Acceleration in m/s²
        
    Returns:
        Force in Newtons
        
    Raises:
        ValueError: If mass or acceleration is negative
    """
    if mass < 0 or acceleration < 0:
        raise ValueError("Mass and acceleration must be non-negative")
    
    return mass * acceleration


# Bad: No types, no docs, unclear
def calc(m, a):
    return m * a
```

### Type Hints

Use type hints everywhere:

```python
from typing import Dict, List, Optional, Union

def process_data(
    items: List[Dict[str, Any]],
    filter_key: Optional[str] = None
) -> Union[List[Dict], Dict[str, int]]:
    """Process data with optional filtering."""
    # Implementation
    pass
```

### Docstrings

Use Google style docstrings:

```python
def complex_function(param1: str, param2: int = 0) -> Dict[str, Any]:
    """
    One-line summary of what the function does.
    
    More detailed explanation if needed. Can span multiple lines
    and include examples.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: 0)
        
    Returns:
        Dictionary containing:
        - key1: Description of key1
        - key2: Description of key2
        
    Raises:
        ValueError: When param1 is empty
        TypeError: When param2 is not an integer
        
    Example:
        >>> result = complex_function("test", 5)
        >>> print(result['key1'])
        'value1'
    """
    pass
```

### Import Organization

```python
# 1. Standard library
import json
import os
from datetime import datetime
from pathlib import Path

# 2. Third-party libraries
import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 3. Local imports
from aurora_x.cache import get_cache
from aurora_x.models import User
```

### Error Handling

```python
# Good: Specific exceptions, proper logging
import logging

logger = logging.getLogger(__name__)

def risky_operation(data: Dict) -> str:
    """Perform operation that might fail."""
    try:
        result = process(data)
        return result
    except KeyError as e:
        logger.error(f"Missing required key: {e}")
        raise ValueError(f"Invalid data structure: {e}")
    except Exception as e:
        logger.exception("Unexpected error in risky_operation")
        raise


# Bad: Bare except, no logging
def bad_operation(data):
    try:
        return process(data)
    except:
        return None
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::test_health_check

# Run with coverage
pytest --cov=aurora_x --cov-report=html

# Run only fast tests
pytest -m "not slow"

# Run in parallel
pytest -n auto
```

### Writing Tests

#### Unit Tests

```python
# tests/test_cache.py
import pytest
from aurora_x.cache import CacheManager


class TestCacheManager:
    """Test suite for CacheManager."""
    
    @pytest.fixture
    def cache(self):
        """Create a test cache instance."""
        return CacheManager(redis_url=None, max_memory_items=100)
    
    def test_set_and_get(self, cache):
        """Test basic set and get operations."""
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
    
    def test_get_nonexistent_key(self, cache):
        """Test getting a key that doesn't exist."""
        assert cache.get("nonexistent") is None
    
    def test_ttl_expiration(self, cache):
        """Test that keys expire after TTL."""
        cache.set("temp", "value", ttl=1)
        time.sleep(2)
        assert cache.get("temp") is None
    
    def test_clear_pattern(self, cache):
        """Test pattern-based cache clearing."""
        cache.set("user:1", "data1")
        cache.set("user:2", "data2")
        cache.set("other:1", "data3")
        
        cache.clear("user:*")
        
        assert cache.get("user:1") is None
        assert cache.get("user:2") is None
        assert cache.get("other:1") == "data3"
```

#### Integration Tests

```python
# tests/test_api_integration.py
import pytest
from fastapi.testclient import TestClient
from aurora_x.serve import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestAPIIntegration:
    """Integration tests for API endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json()["ok"] is True
    
    def test_solver_endpoint(self, client):
        """Test solver with valid input."""
        response = client.post(
            "/api/solve",
            json={"text": "What is 2 + 2?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "result" in data
    
    def test_nl_compile_endpoint(self, client):
        """Test natural language compilation."""
        response = client.post(
            "/api/nl/compile",
            json={"prompt": "Create a function to add two numbers"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["files_generated"]) > 0
```

#### Mocking

```python
# tests/test_with_mocks.py
from unittest.mock import Mock, patch
import pytest


def test_external_api_call():
    """Test function that calls external API."""
    with patch('requests.get') as mock_get:
        # Setup mock
        mock_get.return_value.json.return_value = {"data": "mocked"}
        mock_get.return_value.status_code = 200
        
        # Call function
        result = fetch_external_data()
        
        # Verify
        assert result == {"data": "mocked"}
        mock_get.assert_called_once()


def test_database_query():
    """Test function with database dependency."""
    mock_db = Mock()
    mock_db.query.return_value = [{"id": 1, "name": "test"}]
    
    result = get_users(mock_db)
    
    assert len(result) == 1
    assert result[0]["name"] == "test"
```

### Test Coverage

Aim for >80% code coverage:

```bash
# Generate coverage report
pytest --cov=aurora_x --cov-report=term-missing

# View HTML report
pytest --cov=aurora_x --cov-report=html
open htmlcov/index.html
```

---

## Contributing

### Getting Started

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

### Branch Naming

```
feature/add-new-solver-domain
fix/cache-invalidation-bug
docs/update-api-reference
refactor/improve-performance
```

### Commit Messages

Follow conventional commits:

```
feat: add chemistry solver domain
fix: resolve cache invalidation issue
docs: update API reference for solver
refactor: improve cache performance
test: add tests for solver engine
chore: update dependencies
```

### Pull Request Process

1. **Before submitting:**
   ```bash
   # Run tests
   pytest
   
   # Check code style
   black aurora_x tests
   pylint aurora_x
   
   # Type checking
   mypy aurora_x
   
   # Run all checks
   pre-commit run --all-files
   ```

2. **PR Description Template:**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] Unit tests pass
   - [ ] Integration tests pass
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Comments added for complex code
   - [ ] Documentation updated
   - [ ] No new warnings
   ```

3. **Review Process:**
   - Automated checks must pass
   - At least one reviewer approval
   - No unresolved conversations
   - Up-to-date with main branch

### Code Review Guidelines

**As a reviewer:**
- Be constructive and respectful
- Focus on code quality, not style (that's automated)
- Suggest improvements, don't demand
- Approve when it meets standards

**As an author:**
- Respond to all comments
- Don't take feedback personally
- Ask questions if unclear
- Update based on feedback

---

## Module Documentation

### Cache Module (`aurora_x/cache.py`)

**Purpose:** Centralized caching with Redis/memory fallback

**Key Classes:**
- `CacheManager`: Main cache interface

**Usage:**
```python
from aurora_x.cache import get_cache, cached

# Get cache instance
cache = get_cache()

# Basic operations
cache.set("key", "value", ttl=300)
value = cache.get("key")
cache.delete("key")

# Decorator
@cached(ttl=600, key_prefix="user")
def get_user(user_id: int):
    return db.query_user(user_id)
```

### Solver Module (`aurora_x/generators/solver.py`)

**Purpose:** Multi-domain problem solving

**Key Functions:**
- `solve_text(text: str) -> Dict`: Main solver entry point

**Supported Domains:**
- mathematics
- physics
- chemistry
- logic
- units

**Usage:**
```python
from aurora_x.generators.solver import solve_text

result = solve_text("What is 2 + 2?")
print(result['result'])  # 4
```

### Performance Module (`aurora_x/performance.py`)

**Purpose:** Request performance tracking

**Key Classes:**
- `PerformanceMiddleware`: FastAPI middleware

**Usage:**
```python
from fastapi import FastAPI
from aurora_x.performance import PerformanceMiddleware

app = FastAPI()
app.add_middleware(PerformanceMiddleware, slow_request_threshold=1.0)
```

---

## Extending Aurora-X

### Adding a New Solver Domain

```python
# 1. Create domain file
# aurora_x/generators/domains/biology.py

def detect_biology_task(text: str) -> Optional[str]:
    """Detect if text is a biology problem."""
    if "dna" in text.lower() or "protein" in text.lower():
        return "biology"
    return None

def solve_biology(text: str) -> Dict[str, Any]:
    """Solve biology problems."""
    # Implementation
    return {
        "ok": True,
        "domain": "biology",
        "result": result
    }

# 2. Register in solver.py
from aurora_x.generators.domains import biology

DOMAIN_SOLVERS = {
    "biology": biology.solve_biology,
    # ... other domains
}
```

### Adding a New API Endpoint

```python
# 1. Create endpoint file
# aurora_x/api/new_feature.py

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/new-feature", tags=["new-feature"])

class FeatureRequest(BaseModel):
    data: str

@router.post("/process")
async def process_feature(request: FeatureRequest):
    """Process new feature request."""
    result = process(request.data)
    return {"result": result}

# 2. Register in serve.py
from aurora_x.api.new_feature import router as new_feature_router
app.include_router(new_feature_router)
```

### Adding a New Cache Strategy

```python
# aurora_x/cache_strategies.py

class LFUCache:
    """Least Frequently Used cache strategy."""
    
    def __init__(self, max_size: int):
        self.max_size = max_size
        self.cache = {}
        self.frequency = {}
    
    def get(self, key: str):
        if key in self.cache:
            self.frequency[key] += 1
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        if len(self.cache) >= self.max_size:
            # Evict least frequently used
            lfu_key = min(self.frequency, key=self.frequency.get)
            del self.cache[lfu_key]
            del self.frequency[lfu_key]
        
        self.cache[key] = value
        self.frequency[key] = 1
```

---

## Debugging

### Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Use in code
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.exception("Error with traceback")
```

### Debug Mode

```bash
# Enable debug mode
export DEBUG=true
python -m aurora_x.serve

# Debug specific module
export LOG_LEVEL=DEBUG
export DEBUG_MODULE=aurora_x.solver
python -m aurora_x.serve
```

### Using pdb

```python
# Insert breakpoint
import pdb; pdb.set_trace()

# Or use built-in (Python 3.7+)
breakpoint()
```

### Profiling

```bash
# Profile API endpoint
python -m cProfile -o profile.stats -m aurora_x.serve

# Analyze results
python -m pstats profile.stats
>>> sort cumtime
>>> stats 20
```

---

## Release Process

### Version Numbering

Follow Semantic Versioning (SemVer):
- MAJOR.MINOR.PATCH (e.g., 3.0.0)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Release Checklist

1. **Update version:**
   ```python
   # aurora_x/__init__.py
   __version__ = "3.1.0"
   ```

2. **Update CHANGELOG.md:**
   ```markdown
   ## [3.1.0] - 2025-11-10
   
   ### Added
   - New chemistry solver domain
   
   ### Fixed
   - Cache invalidation bug
   
   ### Changed
   - Improved performance by 20%
   ```

3. **Run full test suite:**
   ```bash
   pytest
   pytest --cov=aurora_x
   ```

4. **Build and test Docker image:**
   ```bash
   docker build -t aurora-x:3.1.0 .
   docker run -p 5002:5002 aurora-x:3.1.0
   ```

5. **Tag release:**
   ```bash
   git tag -a v3.1.0 -m "Release version 3.1.0"
   git push origin v3.1.0
   ```

6. **Create GitHub release:**
   - Go to Releases on GitHub
   - Create new release from tag
   - Add release notes
   - Attach built artifacts

---

## Additional Resources

- **API Reference:** [API_REFERENCE.md](API_REFERENCE.md)
- **User Guide:** [USER_GUIDE.md](USER_GUIDE.md)
- **Deployment Guide:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Performance Guide:** [PERFORMANCE_GUIDE.md](PERFORMANCE_GUIDE.md)
- **GitHub Repository:** https://github.com/chango112595-cell/Aurora-x

---

**Questions or need help?** Open an issue on GitHub!

*Last Updated: November 10, 2025*
