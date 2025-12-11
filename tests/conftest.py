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
    import random
    import string
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return {
        "organization_name": f"test_org_{random_suffix}",
        "email": f"test_{random_suffix}@example.com",
        "password": "TestPass123"
    }

@pytest.fixture(scope="module")
def auth_headers(client, test_org_data):
    """Get authentication headers with valid JWT token."""
    # Create organization first (ignore if already exists)
    create_response = client.post("/org/create", json=test_org_data)
    
    # Login to get token (this should always work)
    login_response = client.post("/admin/login", json={
        "email": test_org_data["email"],
        "password": test_org_data["password"]
    })
    
    # Check if login was successful
    if login_response.status_code != 200:
        # If first org creation failed due to duplicate, try with a new random org
        import random
        import string
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        new_org_data = {
            "organization_name": f"test_org_{random_suffix}",
            "email": f"test_{random_suffix}@example.com",
            "password": "TestPass123"
        }
        client.post("/org/create", json=new_org_data)
        login_response = client.post("/admin/login", json={
            "email": new_org_data["email"],
            "password": new_org_data["password"]
        })
    
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
