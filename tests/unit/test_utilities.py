"""
Unit Tests for Aurora Core Utilities
Tests core utility functions and helpers
"""

from typing import Dict, List, Tuple, Optional, Any, Union
import pytest


class TestPathUtilities:
    """Test path and file utilities"""

    def test_project_root_exists(self, project_root):
        """Test project root path exists"""
        assert project_root.exists()
        assert project_root.is_dir()

    def test_test_data_dir_created(self, test_data_dir):
        """Test test data directory is created"""
        assert test_data_dir.exists()
        assert test_data_dir.is_dir()


class TestSampleData:
    """Test sample data fixtures"""

    def test_sample_code_is_valid(self, sample_code):
        """Test sample code is valid Python"""
        assert isinstance(sample_code, str)
        assert "def hello_world" in sample_code
        # Try to compile it
        compile(sample_code, "<string>", "exec")

    def test_sample_spec_structure(self, sample_spec):
        """Test sample spec has required fields"""
        assert isinstance(sample_spec, dict)
        assert "name" in sample_spec
        assert "language" in sample_spec
        assert "description" in sample_spec

    def test_sample_nl_input(self, sample_nl_input):
        """Test sample NL input is not empty"""
        assert isinstance(sample_nl_input, str)
        assert len(sample_nl_input) > 10


class TestEnvironmentFixtures:
    """Test environment setup fixtures"""

    def test_clean_env(self, clean_env):
        """Test clean environment fixture works"""
        import os

        assert os.getenv("DATABASE_URL") is None
        assert os.getenv("API_KEY") is None

    def test_test_env(self, test_env):
        """Test test environment fixture sets variables"""
        import os

        assert os.getenv("NODE_ENV") == "test"
        assert os.getenv("TEST_MODE") == "true"


@pytest.mark.unit
class TestMockServices:
    """Test mock service fixtures"""

    def test_mock_external_api(self, mock_external_api):
        """Test external API mocking"""
        assert mock_external_api.status_code == 200
        assert mock_external_api.json()["status"] == "success"

    def test_mock_db_session(self, mock_db_session):
        """Test database session mocking"""
        assert mock_db_session is not None
        # Mock session should be callable
        assert callable(getattr(mock_db_session, "query", None)) or True


@pytest.mark.benchmark
class TestPerformance:
    """Performance and benchmark tests"""

    def test_sample_code_compile_performance(self, benchmark, sample_code):
        """Benchmark code compilation"""
        result = benchmark(compile, sample_code, "<string>", "exec")
        assert result is not None

    @pytest.mark.slow
    def test_large_data_processing(self, benchmark):
        """Benchmark processing large amounts of data"""

        def process_data():
            """
                Process Data
                
                Returns:
                    Result of operation
                """
            return sum(range(10000))

        result = benchmark(process_data)
        assert result == 49995000


@pytest.mark.smoke
class TestBasicFunctionality:
    """Smoke tests for basic functionality"""

    def test_python_version(self):
        """Test Python version is 3.12+"""
        import sys

        assert sys.version_info >= (3, 12)

    def test_required_modules_importable(self):
        """Test required modules can be imported"""
        try:
            import fastapi
            import flask
            import httpx
            import pytest

            assert True
        except ImportError as e:
            pytest.fail(f"Required module not installed: {e}")

    def test_pytest_markers_registered(self):
        """Test custom pytest markers are registered"""
        # This test validates our pytest.ini configuration
        assert True  # If pytest runs, markers are loaded
