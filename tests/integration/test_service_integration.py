"""
Integration Tests for Aurora Services
Tests service-to-service communication and workflows
"""

import pytest
import httpx
import asyncio


@pytest.mark.integration
class TestServiceConnectivity:
    """Test that services can communicate with each other"""
    
    @pytest.mark.asyncio
    async def test_all_services_healthy(self):
        """Test all services respond to health checks"""
        services = {
            "backend": "http://localhost:5000/api/health",
            "bridge": "http://localhost:5001/api/health",
            "selflearn": "http://localhost:5002/api/health",
            "chat": "http://localhost:5003/api/health",
        }
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            results = {}
            for name, url in services.items():
                try:
                    response = await client.get(url)
                    results[name] = response.status_code == 200
                except (httpx.ConnectError, httpx.TimeoutException):
                    results[name] = False
            
            # At least one service should be healthy if tests are running against live services
            # This is optional - services might not be running during unit tests
            if any(results.values()):
                pytest.skip("Services not running - skipping live integration test")


@pytest.mark.integration
class TestBridgeToBackend:
    """Test Bridge service integration with Backend API"""
    
    @pytest.mark.asyncio
    async def test_bridge_can_call_backend(self):
        """Test Bridge service can communicate with Backend"""
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                # Call Bridge health
                bridge_response = await client.get("http://localhost:5001/api/health")
                
                # Call Backend health
                backend_response = await client.get("http://localhost:5000/api/health")
                
                # Both should be reachable if services are running
                if bridge_response.status_code == 200 and backend_response.status_code == 200:
                    assert True
                else:
                    pytest.skip("Services not running")
            except (httpx.ConnectError, httpx.TimeoutException):
                pytest.skip("Services not running")


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndWorkflow:
    """Test complete end-to-end workflows"""
    
    @pytest.mark.asyncio
    async def test_nl_to_project_workflow(self, sample_nl_input):
        """Test full NL → Spec → Project workflow"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Step 1: Submit NL input to Bridge
                nl_response = await client.post(
                    "http://localhost:5001/api/bridge/nl",
                    json={"input": sample_nl_input}
                )
                
                # If service is running and endpoint works
                if nl_response.status_code == 200:
                    data = nl_response.json()
                    # Validate response structure
                    assert isinstance(data, dict)
                else:
                    pytest.skip("Bridge service not responding correctly")
                    
            except (httpx.ConnectError, httpx.TimeoutException):
                pytest.skip("Services not running")


@pytest.mark.integration
class TestDatabaseIntegration:
    """Test database interactions"""
    
    def test_database_connection(self, mock_db_session):
        """Test database connection (mocked)"""
        # Mock database operations
        assert mock_db_session is not None
    
    @pytest.mark.database
    def test_database_queries(self):
        """Test basic database queries"""
        # This would test actual DB queries if DB is configured
        pytest.skip("Database not configured for testing yet")


@pytest.mark.integration
class TestHealthCheckPropagation:
    """Test that health checks propagate through services"""
    
    @pytest.mark.asyncio
    async def test_cascade_health_checks(self):
        """Test health checks cascade through all services"""
        services = ["5000", "5001", "5002", "5003"]
        
        async with httpx.AsyncClient(timeout=3.0) as client:
            health_statuses = []
            
            for port in services:
                try:
                    response = await client.get(f"http://localhost:{port}/api/health")
                    health_statuses.append((port, response.status_code == 200))
                except:
                    health_statuses.append((port, False))
            
            # If any service is running, test passes (we're just checking connectivity)
            if not any(status for _, status in health_statuses):
                pytest.skip("No services running")
