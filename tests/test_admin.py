"""
Tests for admin authentication endpoints.
"""
import pytest
from fastapi import status

class TestAdminLogin:
    """Tests for POST /admin/login endpoint."""
    
    def test_login_success(self, client):
        """Test successful admin login returns JWT token."""
        # Create organization first
        org_data = {
            "organization_name": "login_test_org",
            "email": "login@example.com",
            "password": "LoginPass123"
        }
        client.post("/org/create", json=org_data)
        
        # Login
        response = client.post("/admin/login", json={
            "email": org_data["email"],
            "password": org_data["password"]
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0
    
    def test_login_invalid_email(self, client):
        """Test login with non-existent email fails."""
        response = client.post("/admin/login", json={
            "email": "nonexistent@example.com",
            "password": "SomePass123"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_invalid_password(self, client):
        """Test login with incorrect password fails."""
        # Create organization
        org_data = {
            "organization_name": "wrong_pass_org",
            "email": "wrongpass@example.com",
            "password": "CorrectPass123"
        }
        client.post("/org/create", json=org_data)
        
        # Try to login with wrong password
        response = client.post("/admin/login", json={
            "email": org_data["email"],
            "password": "WrongPass123"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_missing_fields(self, client):
        """Test login with missing fields returns validation error."""
        response = client.post("/admin/login", json={
            "email": "test@example.com"
            # Missing password
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_invalid_email_format(self, client):
        """Test login with invalid email format fails validation."""
        response = client.post("/admin/login", json={
            "email": "not-an-email",
            "password": "SomePass123"
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestJWTAuthentication:
    """Tests for JWT token authentication."""
    
    def test_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token fails."""
        response = client.put("/org/update", json={
            "email": "new@example.com"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_protected_endpoint_with_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token fails."""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = client.put("/org/update", 
            headers=headers,
            json={"email": "new@example.com"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_protected_endpoint_with_valid_token(self, client, auth_headers):
        """Test accessing protected endpoint with valid token succeeds."""
        response = client.put("/org/update",
            headers=auth_headers,
            json={"email": "updated@example.com"}
        )
        
        # Should not be unauthorized (might fail for other reasons, but not auth)
        assert response.status_code != status.HTTP_401_UNAUTHORIZED
