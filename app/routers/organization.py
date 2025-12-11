"""
API endpoints for organization management.
"""
from fastapi import APIRouter, Depends, status
from app.models.schemas import (
    OrganizationCreate, 
    OrganizationUpdate, 
    OrganizationResponse,
    OrganizationDelete
)
from app.services.organization_service import OrganizationService
from app.db import get_db, DatabaseManager
from app.security.dependencies import get_current_admin
from typing import Dict, Any

router = APIRouter(prefix="/org", tags=["Organization"])


def get_organization_service(db: DatabaseManager = Depends(get_db)) -> OrganizationService:
    """Dependency to get organization service instance."""
    return OrganizationService(db)


@router.post("/create", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_data: OrganizationCreate,
    service: OrganizationService = Depends(get_organization_service)
):
    """
    Create a new organization.
    
    - Validates uniqueness of organization name
    - Creates dynamic collection
    - Creates admin user
    - Returns organization details
    """
    return service.create_organization(org_data)


@router.get("/get/{organization_name}", response_model=OrganizationResponse)
async def get_organization(
    organization_name: str,
    service: OrganizationService = Depends(get_organization_service)
):
    """
    Get organization details by name.
    
    - Input: organization_name (path parameter)
    - Returns: Organization metadata
    """
    return service.get_organization(organization_name)


@router.put("/update", response_model=OrganizationResponse)
async def update_organization(
    update_data: OrganizationUpdate,
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    service: OrganizationService = Depends(get_organization_service)
):
    """
    Update organization details.
    
    - Requires Authentication
    - Validates new name uniqueness
    - Handles collection migration if name changes
    """
    # The admin can only update their own organization
    # We use the organization name from the token or the current name passed in body?
    # The requirement says "Inputs: new organization_name, new email, new password"
    # It implies we are updating the organization the admin belongs to.
    # We should use the organization_name from the token to identify WHICH org to update.
    
    current_org_name = current_admin.get("organization_name")
    admin_id = current_admin.get("admin_id")
    
    if not current_org_name or not admin_id:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    
    return service.update_organization(current_org_name, update_data, admin_id)


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    current_admin: Dict[str, Any] = Depends(get_current_admin),
    service: OrganizationService = Depends(get_organization_service)
):
    """
    Delete the authenticated admin's organization.
    
    - Requires Authentication
    - Automatically deletes the organization associated with the JWT token
    - Only authenticated admin can delete their own organization
    """
    organization_name = current_admin.get("organization_name")
    org_id = current_admin.get("organization_id")
    
    if not organization_name or not org_id:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    
    service.delete_organization(organization_name, org_id)
    return None
