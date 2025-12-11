"""
Tests for health check and application endpoints.
"""
import pytest
from fastapi import status

class TestHealthCheck:
    """Tests for GET /health endpoint."""
    
    def test_health_check_success(self, client):
        """Test health check returns successful response."""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check required fields
        assert "status" in data
        assert "service" in data
        assert "version" in data
        assert "database" in data
        
        # Verify field types
        assert isinstance(data["status"], str)
        assert isinstance(data["service"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["database"], str)
        
        # Status should be either healthy or unhealthy
        assert data["status"] in ["healthy", "unhealthy"]
        
        # Database should be either connected or disconnected
        assert data["database"] in ["connected", "disconnected"]
    
    def test_health_check_no_auth_required(self, client):
        """Test health check endpoint does not require authentication."""
        # Should work without any headers
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK


class TestRootEndpoint:
    """Tests for GET / root endpoint."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns welcome message."""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "message" in data
        assert "docs" in data
        assert "redoc" in data
        assert data["docs"] == "/docs"
        assert data["redoc"] == "/redoc"
