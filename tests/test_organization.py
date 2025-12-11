"""
Tests for organization management endpoints.
"""
import pytest
from fastapi import status

class TestOrganizationCreate:
    """Tests for POST /org/create endpoint."""
    
    def test_create_organization_success(self, client):
        """Test successful organization creation."""
        import random
        import string
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        response = client.post("/org/create", json={
            "organization_name": f"acme_corp_{random_suffix}",
            "email": f"admin_{random_suffix}@acme.com",
            "password": "SecurePass123"
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["organization_name"] == f"acme_corp_{random_suffix}"
        assert data["email"] == f"admin_{random_suffix}@acme.com"
        assert "connection_details" in data
        assert "id" in data
        assert "created_at" in data
    
    def test_create_organization_duplicate_name(self, client):
        """Test creating organization with duplicate name fails."""
        import random
        import string
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        # Create first organization
        org_name = f"duplicate_test_{random_suffix}"
        client.post("/org/create", json={
            "organization_name": org_name,
            "email": f"first_{random_suffix}@example.com",
            "password": "Password123"
        })
        
        # Try to create with same name but different email
        response = client.post("/org/create", json={
            "organization_name": org_name,
            "email": f"second_{random_suffix}@example.com",
            "password": "Password123"
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()
    
    def test_create_organization_invalid_password(self, client):
        """Test creating organization with weak password fails."""
        import random
        import string
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        response = client.post("/org/create", json={
            "organization_name": f"weak_pass_org_{random_suffix}",
            "email": f"weak_{random_suffix}@example.com",
            "password": "weak"  # Too short, no uppercase, no digit
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestOrganizationGet:
    """Tests for GET /org/get endpoint."""
    
    def test_get_organization_success(self, client):
        """Test successful organization retrieval."""
        import random
        import string
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        # Create organization first
        org_name = f"get_test_org_{random_suffix}"
        client.post("/org/create", json={
            "organization_name": org_name,
            "email": f"get_{random_suffix}@example.com",
            "password": "GetPass123"
        })
        
        # Get organization
        response = client.get(f"/org/get?organization_name={org_name}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["organization_name"] == org_name
        assert data["email"] == f"get_{random_suffix}@example.com"
    
    def test_get_organization_not_found(self, client):
        """Test getting non-existent organization returns 404."""
        response = client.get("/org/get?organization_name=nonexistent_org")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestOrganizationUpdate:
    """Tests for PUT /org/update endpoint."""
    
    def test_update_organization_requires_auth(self, client):
        """Test update endpoint requires authentication."""
        response = client.put("/org/update", json={
            "organization_name": "new_name"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_organization_email(self, client, auth_headers):
        """Test updating organization email."""
        response = client.put("/org/update", 
            headers=auth_headers,
            json={"email": "newemail@example.com"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "newemail@example.com"


class TestOrganizationDelete:
    """Tests for DELETE /org/delete endpoint."""
    
    def test_delete_organization_requires_auth(self, client):
        """Test delete endpoint requires authentication."""
        response = client.delete("/org/delete")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_organization_success(self, client):
        """Test successful organization deletion."""
        # Create organization
        org_data = {
            "organization_name": "delete_test_org",
            "email": "delete@example.com",
            "password": "DeletePass123"
        }
        client.post("/org/create", json=org_data)
        
        # Login to get token
        login_response = client.post("/admin/login", json={
            "email": org_data["email"],
            "password": org_data["password"]
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Delete organization
        response = client.delete("/org/delete", headers=headers)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify organization is deleted
        get_response = client.get(f"/org/get?organization_name={org_data['organization_name']}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
