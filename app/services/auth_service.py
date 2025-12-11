"""
Authentication service for handling admin login.
"""
from typing import Optional, Dict, Any
from app.db import DatabaseManager
from app.repositories.admin_repository import AdminRepository
from app.security.password_handler import password_handler
from app.security.jwt_handler import jwt_handler
from app.models.schemas import AdminLogin, TokenResponse
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication logic."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.admin_repo = AdminRepository(db_manager)
    
    def login(self, login_data: AdminLogin) -> Optional[TokenResponse]:
        """
        Authenticate admin user and return JWT token.
        
        Args:
            login_data: Email and password
            
        Returns:
            TokenResponse if credentials are valid, None otherwise
        """
        admin = self.admin_repo.find_by_email(login_data.email)
        
        if not admin:
            logger.warning(f"Login failed: Email not found - {login_data.email}")
            return None
            
        if not password_handler.verify_password(login_data.password, admin['password']):
            logger.warning(f"Login failed: Invalid password - {login_data.email}")
            return None
            
        # Create access token
        token_data = {
            "sub": admin['email'],
            "admin_id": admin['id'],
            "organization_id": admin['organization_id'],
            "organization_name": admin.get('organization_name', '')
        }
        
        access_token = jwt_handler.create_access_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            admin_id=admin['id'],
            organization_id=admin['organization_id'],
            organization_name=admin.get('organization_name', '')
        )
