# 🧪 Aurora-X Testing Guide

**Created by Aurora Autonomous System**  
**Date:** 2025-11-10

## Overview

Aurora-X now has a comprehensive testing infrastructure covering:
- ✅ **Unit Tests** - Individual functions and classes
- ✅ **Integration Tests** - Service interactions
- ✅ **API Tests** - Endpoint validation
- ✅ **E2E Tests** - Complete workflows
- ✅ **Performance Tests** - Benchmarking
- ✅ **Security Tests** - Vulnerability scanning

---

## 📊 Test Coverage Targets

| Component | Current | Target | Status |
|-----------|---------|--------|--------|
| Python Services | TBD | 60%+ | 🟡 In Progress |
| Backend API | TBD | 60%+ | 🟡 In Progress |
| Frontend | TBD | 50%+ | 🟡 In Progress |
| **Overall** | TBD | **60%+** | 🟡 **In Progress** |

---

## 🚀 Quick Start

### Run All Tests

```bash
# Run complete test suite
./run-tests.sh

# Run with coverage
./run-tests.sh all true
```

### Run Specific Test Types

```bash
# Python tests only
./run-tests.sh python

# Unit tests only
./run-tests.sh unit

# Integration tests
./run-tests.sh integration

# Smoke tests (quick validation)
./run-tests.sh smoke
```

### Run Individual Test Files

```bash
# Specific test file
pytest tests/unit/test_bridge_service.py -v

# Specific test class
pytest tests/unit/test_bridge_service.py::TestBridgeHealth -v

# Specific test function
pytest tests/unit/test_bridge_service.py::TestBridgeHealth::test_health_endpoint -v
```

---

## 📁 Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests (fast, isolated)
│   ├── test_bridge_service.py
│   ├── test_selflearn_server.py
│   └── test_utilities.py
├── integration/             # Integration tests (slower, requires services)
│   └── test_service_integration.py
├── e2e/                     # End-to-end tests (slowest, full system)
│   └── (future E2E tests)
└── fixtures/                # Test data and fixtures
    └── data/
```

---

## 🎯 Test Markers

Organize and filter tests using pytest markers:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only smoke tests
pytest -m smoke

# Run only fast tests (exclude slow)
pytest -m "not slow"

# Run Bridge service tests
pytest -m bridge

# Run async tests
pytest -m async
```

### Available Markers

- `unit` - Fast, isolated unit tests
- `integration` - Service interaction tests
- `e2e` - End-to-end workflow tests
- `slow` - Tests taking >1 second
- `api` - API endpoint tests
- `database` - Tests requiring database
- `async` - Asynchronous tests
- `smoke` - Quick validation tests
- `security` - Security-related tests
- `performance` - Performance/benchmark tests
- `bridge` - Bridge service tests
- `selflearn` - Self-learn server tests
- `chat` - Chat server tests
- `backend` - Backend API tests
- `frontend` - Frontend tests

---

## 🔧 Test Configuration

### pytest.ini

Main pytest configuration in `/pytest.ini`:
- Test discovery patterns
- Coverage settings (60% minimum)
- Parallel execution enabled
- HTML and JSON reports
- Custom markers

### conftest.py

Shared test fixtures in `/tests/conftest.py`:
- Service test clients (Bridge, Self-Learn)
- Mock data fixtures
- Database fixtures
- Environment setup
- Cleanup utilities

---

## 📊 Coverage Reports

### Generate Coverage

```bash
# Run with coverage
pytest --cov --cov-report=html

# View HTML report
python3 -m http.server -d htmlcov 8080
# Open: http://localhost:8080
```

### Coverage Files Generated

- `htmlcov/index.html` - Interactive HTML report
- `coverage.json` - Machine-readable JSON
- `coverage.xml` - XML for CI/CD tools
- Terminal output - Summary in console

### Coverage Configuration

Minimum coverage threshold: **60%**

Excluded from coverage:
- Test files (`tests/*`, `*_test.py`)
- Migrations
- Virtual environments
- Node modules
- Build outputs

---

## 🧩 Writing Tests

### Unit Test Example

```python
import pytest

class TestMyFeature:
    """Test suite for my feature"""
    
    def test_basic_functionality(self):
        """Test basic functionality works"""
        result = my_function(input_value)
        assert result == expected_value
    
    @pytest.mark.slow
    def test_performance(self, benchmark):
        """Benchmark performance"""
        result = benchmark(my_function, input_value)
        assert result is not None
```

### Integration Test Example

```python
import pytest
import httpx

@pytest.mark.integration
class TestServiceIntegration:
    """Integration tests for services"""
    
    @pytest.mark.asyncio
    async def test_service_communication(self):
        """Test services can communicate"""
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:5001/api/health")
            assert response.status_code == 200
```

### Using Fixtures

```python
def test_with_fixtures(bridge_client, sample_spec):
    """Test using provided fixtures"""
    response = bridge_client.post("/api/bridge/spec", json=sample_spec)
    assert response.status_code in [200, 201]
```

---

## 🤖 Automated Testing (CI/CD)

### GitHub Actions Workflow

Tests run automatically on:
- Every push to `main` or `develop`
- Every pull request
- Manual workflow dispatch

### CI/CD Test Jobs

1. **Python Tests** - Unit and integration tests for Python services
2. **Backend Tests** - Node.js API tests
3. **Frontend Tests** - React component tests
4. **Integration Tests** - Multi-service workflows
5. **Docker Tests** - Dockerfile build validation
6. **Security Scan** - Bandit, Safety, vulnerability checks
7. **Code Quality** - Linting and formatting checks

### Viewing CI Results

- GitHub Actions tab shows test results
- Coverage reports uploaded to Codecov
- Test artifacts available for download
- Failed tests block PR merges

---

## 🔒 Security Testing

### Run Security Scans

```bash
# Install security tools
pip install -r requirements-security.txt

# Run Bandit (Python security scanner)
bandit -r aurora_x/ tools/ -f txt

# Run Safety (dependency vulnerabilities)
safety check

# Run pip-audit (package auditing)
pip-audit
```

### Security Tools Included

- **Bandit** - Python AST-based security linter
- **Safety** - Dependency vulnerability scanner
- **pip-audit** - Audit Python packages
- **Semgrep** - Static analysis security testing
- **detect-secrets** - Prevent secrets in code

---

## 📈 Performance Testing

### Benchmark Tests

```python
@pytest.mark.benchmark
def test_performance(benchmark):
    """Benchmark function performance"""
    result = benchmark(expensive_function, arg1, arg2)
    assert result is not None
```

### Load Testing (Future)

Using Locust for load testing:
```bash
locust -f tests/performance/locustfile.py
```

---

## 🐛 Debugging Tests

### Verbose Output

```bash
# Very verbose (-vv)
pytest tests/ -vv

# Show local variables in failures
pytest tests/ -l

# Stop on first failure
pytest tests/ -x

# Drop into debugger on failure
pytest tests/ --pdb
```

### Useful Debugging Options

```bash
# Show print statements
pytest tests/ -s

# Show test durations
pytest tests/ --durations=10

# Run last failed tests only
pytest tests/ --lf

# Run failed tests first, then others
pytest tests/ --ff
```

---

## 📝 Test Best Practices

### DO ✅

- Write descriptive test names
- Use fixtures for setup/teardown
- Test edge cases and error conditions
- Keep tests fast and isolated
- Use appropriate markers
- Mock external dependencies
- Document complex test logic
- Aim for >60% coverage

### DON'T ❌

- Write tests that depend on other tests
- Test implementation details
- Make network calls in unit tests
- Use hardcoded paths or values
- Ignore test failures
- Skip coverage for new code
- Write slow unit tests
- Test third-party libraries

---

## 🎯 Test Checklist

When adding new features:

- [ ] Write unit tests for new functions
- [ ] Write integration tests for new APIs
- [ ] Update fixtures if needed
- [ ] Add appropriate markers
- [ ] Run tests locally before committing
- [ ] Ensure coverage doesn't decrease
- [ ] Update documentation if needed

---

## 📊 Current Test Status

### Tests Implemented

✅ **Unit Tests:**
- Bridge Service health checks
- Bridge Service NL/Spec endpoints
- Self-Learn Server health checks
- Self-Learn Server control endpoints
- Utility functions and fixtures

✅ **Integration Tests:**
- Service connectivity tests
- Health check propagation
- Database integration (mocked)

✅ **Infrastructure:**
- pytest configuration
- Test fixtures (conftest.py)
- Coverage reporting
- GitHub Actions CI/CD
- Test runner script

### Tests Pending

⏳ **Unit Tests:**
- Backend API routes
- Frontend components
- Database models
- Middleware functions

⏳ **Integration Tests:**
- Full NL→Project workflow
- Service-to-service communication
- Database operations

⏳ **E2E Tests:**
- User workflows
- Multi-service scenarios

---

## 🚀 Next Steps

### Immediate (Ready Now)

1. **Run Test Suite**
   ```bash
   ./run-tests.sh
   ```

2. **Check Coverage**
   ```bash
   pytest --cov --cov-report=html
   open htmlcov/index.html
   ```

3. **Add Tests for New Features**
   - Copy existing test patterns
   - Use provided fixtures
   - Run tests locally

### Short-Term (This Week)

4. **Increase Coverage**
   - Add tests for core utilities
   - Test error handling
   - Add edge case tests

5. **Frontend Testing**
   - Set up Jest properly
   - Add React component tests
   - Add integration tests

### Long-Term (Next 2 Weeks)

6. **E2E Testing**
   - Set up Playwright/Cypress
   - Add critical user flows
   - Integrate with CI/CD

7. **Performance Testing**
   - Add load tests with Locust
   - Benchmark critical paths
   - Set performance budgets

---

## 🌌 Aurora's Notes

**Testing Philosophy:**
"Tests are not just about catching bugs - they're about confidence.
Good tests enable fearless refactoring, rapid iteration, and safe
deployments. Invest in tests now, save debugging time later."

**Current Status:**
- ✅ Test infrastructure complete
- ✅ Sample tests demonstrate patterns
- ✅ CI/CD automation configured
- ⏳ Coverage TBD (need to run tests)
- ⏳ More tests needed for full coverage

**Next Priority:**
Run the test suite to establish baseline coverage, then systematically
add tests to reach 60%+ target. Focus on critical paths first:
health checks, API endpoints, core business logic.

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-10  
**Created By:** Aurora Autonomous System 🧪✨
