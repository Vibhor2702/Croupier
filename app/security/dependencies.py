"""
Authentication dependencies for FastAPI routes.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
from app.security.jwt_handler import jwt_handler

security = HTTPBearer(auto_error=False)


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to extract and verify JWT token from request.
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        Decoded token payload containing admin_id and organization_id
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = jwt_handler.verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract required fields
    admin_id = payload.get("admin_id")
    organization_id = payload.get("organization_id")
    
    if not admin_id or not organization_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "admin_id": admin_id,
        "organization_id": organization_id,
        "organization_name": payload.get("organization_name", "")
    }
