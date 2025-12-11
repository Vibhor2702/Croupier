"""
Test configuration and fixtures for Croupier tests.
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from app.db import db_manager

@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="module")
def test_org_data():
    """Sample organization data for testing."""
    return {
        "organization_name": "test_org",
        "email": "test@example.com",
        "password": "TestPass123"
    }

@pytest.fixture(scope="module")
def auth_headers(client, test_org_data):
    """Get authentication headers with valid JWT token."""
    # Create organization first
    client.post("/org/create", json=test_org_data)
    
    # Login to get token
    response = client.post("/admin/login", json={
        "email": test_org_data["email"],
        "password": test_org_data["password"]
    })
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}
