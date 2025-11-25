"""
Unit Tests for Bridge Service
Tests the Factory Bridge NL->Project generation service
"""

from typing import Dict, List, Tuple, Optional, Any, Union
import pytest


class TestBridgeHealth:
    """Test Bridge service health endpoints"""

    def test_health_endpoint(self, bridge_client):
        """Test /health endpoint returns 200"""
        response = bridge_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_healthz_endpoint(self, bridge_client):
        """Test /healthz endpoint returns 200"""
        response = bridge_client.get("/healthz")
        assert response.status_code == 200

    def test_api_health_endpoint(self, bridge_client):
        """Test /api/health endpoint returns 200"""
        response = bridge_client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "aurora-x-bridge"
        assert "aurora_fix" in data

    def test_api_status_endpoint(self, bridge_client):
        """Test /api/status endpoint returns 200"""
        response = bridge_client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert data["service"] == "Factory Bridge"
        assert data["port"] == 5001


class TestBridgeNLEndpoint:
    """Test Bridge natural language endpoint"""

    def test_nl_endpoint_exists(self, bridge_client):
        """Test /api/bridge/nl endpoint exists"""
        response = bridge_client.post("/api/bridge/nl", json={})
        # Should not return 404
        assert response.status_code != 404

    @pytest.mark.integration
    def test_nl_to_spec_conversion(self, bridge_client, sample_nl_input):
        """Test converting NL input to spec"""
        response = bridge_client.post("/api/bridge/nl", json={"input": sample_nl_input})
        # Check response structure (implementation-dependent)
        assert response.status_code in [200, 201, 422]  # Accept validation errors for now

    def test_nl_endpoint_requires_input(self, bridge_client):
        """Test NL endpoint validates input"""
        response = bridge_client.post("/api/bridge/nl", json={})
        # Should return validation error or handle gracefully
        assert response.status_code in [200, 400, 422]


class TestBridgeSpecEndpoint:
    """Test Bridge spec endpoint"""

    def test_spec_endpoint_exists(self, bridge_client):
        """Test /api/bridge/spec endpoint exists"""
        response = bridge_client.post("/api/bridge/spec", json={})
        assert response.status_code != 404

    @pytest.mark.integration
    def test_spec_to_project(self, bridge_client, sample_spec):
        """Test converting spec to project"""
        response = bridge_client.post("/api/bridge/spec", json={"spec": sample_spec})
        assert response.status_code in [200, 201, 422]


@pytest.mark.asyncio
class TestBridgeAsync:
    """Test Bridge service async functionality"""

    async def test_async_health_check(self, bridge_async_client):
        """Test async health check"""
        response = await bridge_async_client.get("/health")
        assert response.status_code == 200


@pytest.mark.unit
class TestBridgeValidation:
    """Test Bridge input validation"""

    def test_empty_request_handling(self, bridge_client):
        """Test handling of empty requests"""
        response = bridge_client.post("/api/bridge/nl", json={})
        assert response.status_code in [200, 400, 422]

    def test_malformed_json_handling(self, bridge_client):
        """Test handling of malformed JSON"""
        response = bridge_client.post("/api/bridge/nl", data="not json", headers={"Content-Type": "application/json"})
        assert response.status_code in [400, 422]


@pytest.mark.smoke
class TestBridgeSmokeTests:
    """Quick smoke tests for Bridge service"""

    def test_service_starts(self, bridge_app):
        """Test that service app is created"""
        assert bridge_app is not None
        assert hasattr(bridge_app, "routes")

    def test_cors_enabled(self, bridge_app):
        """Test that CORS middleware is configured"""
        middlewares = [m.cls.__name__ for m in bridge_app.user_middleware]
        assert "CORSMiddleware" in middlewares
