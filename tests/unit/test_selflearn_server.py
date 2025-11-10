"""
Unit Tests for Self-Learn Server
Tests the autonomous self-learning daemon
"""

import pytest


class TestSelfLearnHealth:
    """Test Self-Learn server health endpoints"""

    def test_health_endpoint(self, selflearn_client):
        """Test /health endpoint returns 200"""
        response = selflearn_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_api_health_endpoint(self, selflearn_client):
        """Test /api/health endpoint returns 200"""
        response = selflearn_client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "self-learn"
        assert "aurora_fix" in data


class TestSelfLearnStats:
    """Test Self-Learn statistics endpoint"""

    def test_stats_endpoint(self, selflearn_client):
        """Test /stats endpoint returns statistics"""
        response = selflearn_client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_runs" in data
        assert "successful_runs" in data
        assert "failed_runs" in data


class TestSelfLearnControl:
    """Test Self-Learn daemon control endpoints"""

    def test_start_endpoint(self, selflearn_client):
        """Test /start endpoint"""
        response = selflearn_client.post("/start")
        assert response.status_code in [200, 400]  # May already be running

    def test_stop_endpoint(self, selflearn_client):
        """Test /stop endpoint"""
        response = selflearn_client.post("/stop")
        assert response.status_code in [200, 400]  # May not be running

    def test_status_endpoint(self, selflearn_client):
        """Test /status endpoint"""
        response = selflearn_client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert "running" in data or "status" in data


class TestSelfLearnRecentRuns:
    """Test Self-Learn recent runs endpoint"""

    def test_recent_runs_endpoint(self, selflearn_client):
        """Test /recent-runs endpoint"""
        response = selflearn_client.get("/recent-runs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))


@pytest.mark.integration
class TestSelfLearnIntegration:
    """Integration tests for Self-Learn server"""

    def test_daemon_lifecycle(self, selflearn_client):
        """Test full daemon lifecycle: start → status → stop"""
        # Start daemon
        start_response = selflearn_client.post("/start")
        assert start_response.status_code in [200, 400]

        # Check status
        status_response = selflearn_client.get("/status")
        assert status_response.status_code == 200

        # Get stats
        stats_response = selflearn_client.get("/stats")
        assert stats_response.status_code == 200

        # Stop daemon
        stop_response = selflearn_client.post("/stop")
        assert stop_response.status_code in [200, 400]


@pytest.mark.smoke
class TestSelfLearnSmoke:
    """Quick smoke tests for Self-Learn server"""

    def test_service_starts(self, selflearn_app):
        """Test that service app is created"""
        assert selflearn_app is not None
        assert hasattr(selflearn_app, "routes")

    def test_all_endpoints_exist(self, selflearn_client):
        """Test all expected endpoints are registered"""
        expected_paths = ["/health", "/api/health", "/stats", "/status", "/start", "/stop", "/recent-runs"]

        for path in expected_paths:
            # Try GET first
            response = selflearn_client.get(path)
            if response.status_code == 405:  # Method not allowed, try POST
                response = selflearn_client.post(path)

            assert response.status_code != 404, f"Endpoint {path} not found"
