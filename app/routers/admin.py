"""
API endpoints for admin authentication.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import AdminLogin, TokenResponse, ErrorResponse
from app.services.auth_service import AuthService
from app.db import get_db, DatabaseManager

router = APIRouter(prefix="/admin", tags=["Admin"])


def get_auth_service(db: DatabaseManager = Depends(get_db)) -> AuthService:
    """Dependency to get auth service instance."""
    return AuthService(db)


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: AdminLogin,
    service: AuthService = Depends(get_auth_service)
):
    """
    Admin login endpoint.
    
    - Validates credentials
    - Returns signed JWT containing admin_id + organization_id
    """
    token = service.login(login_data)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token
