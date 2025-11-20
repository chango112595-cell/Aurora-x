"""
Pytest Configuration and Shared Fixtures
Provides reusable test fixtures for all test modules
"""

import asyncio
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

# ============================================
# Pytest Configuration
# ============================================


def pytest_configure(config):
    """Configure pytest with custom settings"""
    config.addinivalue_line(
        "markers", "requires_network: Tests that require network access")
    config.addinivalue_line("markers", "requires_gpu: Tests that require GPU")


# ============================================
# Path Fixtures
# ============================================


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data_dir(project_root) -> Path:
    """Get the test data directory"""
    data_dir = project_root / "tests" / "fixtures" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


# ============================================
# Bridge Service Fixtures
# ============================================


@pytest.fixture(scope="module")
def bridge_app():
    """Create Bridge service FastAPI app for testing"""
    from aurora_x.bridge.service import app

    return app


@pytest.fixture
def bridge_client(bridge_app) -> Generator[TestClient, None, None]:
    """Create Bridge service test client"""
    with TestClient(bridge_app) as client:
        yield client


@pytest.fixture
async def bridge_async_client(_bridge_app) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create async Bridge service test client"""
    async with httpx.AsyncClient(base_url="http://test") as client:
        yield client


# ============================================
# Self-Learn Server Fixtures
# ============================================


@pytest.fixture(scope="module")
def selflearn_app():
    """Create Self-Learn server FastAPI app for testing"""
    from aurora_x.self_learn_server import app

    return app


@pytest.fixture
def selflearn_client(selflearn_app) -> Generator[TestClient, None, None]:
    """Create Self-Learn server test client"""
    with TestClient(selflearn_app) as client:
        yield client


# ============================================
# Mock Data Fixtures
# ============================================


@pytest.fixture
def input_data():
    """Sample input data for test functions"""
    return {"text": "test input", "value": 42}


@pytest.fixture
def items():
    """Sample list of items for batch test functions"""
    return [
        {"id": 1, "input": "item1"},
        {"id": 2, "input": "item2"},
        {"id": 3, "input": "item3"},
    ]


@pytest.fixture
def sample_code():
    """Sample Python code for testing"""
    return '''
def hello_world(name: str) -> str:
    """Greet someone by name"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(hello_world("Aurora"))
'''


@pytest.fixture
def sample_spec():
    """Sample project specification for testing"""
    return {
        "name": "test-project",
        "description": "A test project for Aurora",
        "language": "python",
        "features": ["cli", "api"],
        "dependencies": ["fastapi", "pytest"],
    }


@pytest.fixture
def sample_nl_input():
    """Sample natural language input for testing"""
    return "Create a simple REST API with FastAPI that has health check and status endpoints"


# ============================================
# Database Fixtures
# ============================================


@pytest.fixture
def mock_db_session():
    """Mock database session for testing"""
    from unittest.mock import MagicMock

    session = MagicMock()
    return session


# ============================================
# Environment Fixtures
# ============================================


@pytest.fixture
def clean_env(monkeypatch):
    """Clean environment variables for testing"""
    # Remove any environment variables that might interfere
    env_vars = ["DATABASE_URL", "API_KEY", "SECRET_KEY"]
    for var in env_vars:
        monkeypatch.delenv(var, raising=False)
    yield
    # Cleanup happens automatically with monkeypatch


@pytest.fixture
def test_env(monkeypatch):
    """Set up test environment variables"""
    monkeypatch.setenv("NODE_ENV", "test")
    monkeypatch.setenv("PYTHONUNBUFFERED", "1")
    monkeypatch.setenv("TEST_MODE", "true")
    yield


# ============================================
# Async Fixtures
# ============================================


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


# ============================================
# Cleanup Fixtures
# ============================================


@pytest.fixture(autouse=True)
def cleanup_temp_files(_tmp_path, project_root):
    """Clean up temporary test files after each test"""
    yield
    # Cleanup temp test files
    temp_patterns = ["test_*.tmp", "*.test.json", "test_output_*"]
    for pattern in temp_patterns:
        for file in project_root.glob(f"**/{pattern}"):
            if file.is_file():
                file.unlink()


# ============================================
# Performance Fixtures
# ============================================


@pytest.fixture
def benchmark_config():
    """Configuration for benchmark tests"""
    return {"min_rounds": 5, "min_time": 0.01, "max_time": 1.0, "warmup": True}


# ============================================
# Mock Service Fixtures
# ============================================


@pytest.fixture
def mock_external_api(_monkeypatch):
    """Mock external API calls"""
    from unittest.mock import MagicMock, patch

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}

    with patch("httpx.get", return_value=mock_response):
        with patch("httpx.post", return_value=mock_response):
            yield mock_response
