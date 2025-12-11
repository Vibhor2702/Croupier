"""
Tests for organization management endpoints.
"""
import pytest
from fastapi import status

class TestOrganizationCreate:
    """Tests for POST /org/create endpoint."""
    
    def test_create_organization_success(self, client):
        """Test successful organization creation."""
        response = client.post("/org/create", json={
            "organization_name": "acme_corp",
            "email": "admin@acme.com",
            "password": "SecurePass123"
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["organization_name"] == "acme_corp"
        assert data["email"] == "admin@acme.com"
        assert "connection_details" in data
        assert "id" in data
        assert "created_at" in data
    
    def test_create_organization_duplicate_name(self, client):
        """Test creating organization with duplicate name fails."""
        # Create first organization
        client.post("/org/create", json={
            "organization_name": "duplicate_test",
            "email": "first@example.com",
            "password": "Password123"
        })
        
        # Try to create with same name
        response = client.post("/org/create", json={
            "organization_name": "duplicate_test",
            "email": "second@example.com",
            "password": "Password123"
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()
    
    def test_create_organization_invalid_password(self, client):
        """Test creating organization with weak password fails."""
        response = client.post("/org/create", json={
            "organization_name": "weak_pass_org",
            "email": "weak@example.com",
            "password": "weak"  # Too short, no uppercase, no digit
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestOrganizationGet:
    """Tests for GET /org/get endpoint."""
    
    def test_get_organization_success(self, client):
        """Test successful organization retrieval."""
        # Create organization first
        org_name = "get_test_org"
        client.post("/org/create", json={
            "organization_name": org_name,
            "email": "get@example.com",
            "password": "GetPass123"
        })
        
        # Get organization
        response = client.get(f"/org/get?organization_name={org_name}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["organization_name"] == org_name
        assert data["email"] == "get@example.com"
    
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
