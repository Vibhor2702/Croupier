"""
Organization service for handling business logic.
Manages organization lifecycle including dynamic collections.
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError
from app.db import DatabaseManager
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.admin_repository import AdminRepository
from app.models.schemas import OrganizationCreate, OrganizationUpdate, OrganizationResponse
from app.security.password_handler import password_handler
import logging

logger = logging.getLogger(__name__)


class OrganizationService:
    """Service for organization management."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.org_repo = OrganizationRepository(db_manager)
        self.admin_repo = AdminRepository(db_manager)
    
    def create_organization(self, org_data: OrganizationCreate) -> OrganizationResponse:
        """
        Create a new organization and its admin user.
        
        Args:
            org_data: Organization creation data
            
        Returns:
            Created organization details
            
        Raises:
            HTTPException: If organization or email already exists
        """
        # 1. Validate uniqueness
        if self.org_repo.exists(org_data.organization_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Organization '{org_data.organization_name}' already exists"
            )
            
        if self.admin_repo.find_by_email(org_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{org_data.email}' is already registered"
            )
            
        try:
            # 2. Create Organization Metadata
            org_dict = {
                "organization_name": org_data.organization_name,
                "email": org_data.email
            }
            created_org = self.org_repo.create(org_dict)
            
            if not created_org:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create organization record"
                )

            # 3. Create Admin User
            hashed_password = password_handler.hash_password(org_data.password)
            admin_dict = {
                "email": org_data.email,
                "password": hashed_password,
                "organization_id": created_org['id'],
                "organization_name": org_data.organization_name
            }
            self.admin_repo.create(admin_dict)
            
            # 4. Create Dynamic Collection (initialize with an index)
            # This ensures the collection exists
            org_collection = self.db_manager.get_org_collection(org_data.organization_name)
            # Create a dummy index to ensure collection creation
            org_collection.create_index("created_at")
            
            logger.info(f"Successfully created organization: {org_data.organization_name}")
            
            return OrganizationResponse(
                id=str(created_org['id']),
                organization_name=str(created_org['organization_name']),
                email=str(created_org['email']),
                created_at=created_org['created_at'],
                updated_at=created_org.get('updated_at')
            )
            
        except DuplicateKeyError as e:
            logger.error(f"Duplicate key error during creation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization or email already exists"
            )
        except Exception as e:
            logger.error(f"Error creating organization: {str(e)}")
            # Cleanup if possible (omitted for simplicity, but in prod we'd want rollback)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during organization creation"
            )

    def get_organization(self, organization_name: str) -> OrganizationResponse:
        """
        Get organization details by name.
        
        Args:
            organization_name: Name of the organization
            
        Returns:
            Organization details
            
        Raises:
            HTTPException: If organization not found
        """
        org = self.org_repo.find_by_name(organization_name)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization '{organization_name}' not found"
            )
        return OrganizationResponse(**org)

    def update_organization(
        self, 
        current_org_name: str, 
        update_data: OrganizationUpdate,
        admin_id: str
    ) -> OrganizationResponse:
        """
        Update organization details and handle collection migration if name changes.
        
        Args:
            current_org_name: Current name of the organization
            update_data: New data to update
            admin_id: ID of the admin performing the update
            
        Returns:
            Updated organization details
        """
        # Verify organization exists
        org = self.org_repo.find_by_name(current_org_name)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
            
        # Prepare update dictionary
        fields_to_update = {}
        if update_data.email:
            fields_to_update['email'] = update_data.email
            
        new_name = update_data.organization_name
        rename_collection = False
        
        if new_name and new_name != current_org_name:
            # Check if new name is taken
            if self.org_repo.exists(new_name):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Organization name '{new_name}' is already taken"
                )
            fields_to_update['organization_name'] = new_name
            rename_collection = True
            
        # Update Organization Metadata
        if fields_to_update:
            updated_org = self.org_repo.update(current_org_name, fields_to_update)
        else:
            updated_org = org
            
        # Update Admin User if needed
        admin_updates = {}
        if update_data.email:
            admin_updates['email'] = update_data.email
        if update_data.password:
            admin_updates['password'] = password_handler.hash_password(update_data.password)
        if rename_collection:
            admin_updates['organization_name'] = new_name
            
        if admin_updates:
            self.admin_repo.update(admin_id, admin_updates)
            
        # Handle Collection Migration if name changed
        if rename_collection and new_name:
            self._migrate_collection(current_org_name, str(new_name))
            
        if not updated_org:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update organization record"
            )

        return OrganizationResponse(
            id=str(updated_org['id']),
            organization_name=str(updated_org['organization_name']),
            email=str(updated_org['email']),
            created_at=updated_org['created_at'],
            updated_at=updated_org.get('updated_at')
        )

    def delete_organization(self, organization_name: str, admin_org_id: str) -> Dict[str, str]:
        """
        Delete an organization and all its data.
        
        Args:
            organization_name: Name of the organization to delete
            admin_org_id: Organization ID from the admin's token (for authorization)
            
        Returns:
            Success message
        """
        # Verify organization exists
        org = self.org_repo.find_by_name(organization_name)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
            
        # Authorization check: Ensure admin belongs to this organization
        if org['id'] != admin_org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to delete this organization"
            )
            
        # 1. Delete Admin User
        self.admin_repo.delete_by_organization(org['id'])
        
        # 2. Delete Organization Metadata
        self.org_repo.delete(organization_name)
        
        # 3. Drop Dynamic Collection
        self.db_manager.drop_org_collection(organization_name)
        
        return {"detail": f"Organization '{organization_name}' deleted successfully"}

    def _migrate_collection(self, old_name: str, new_name: str):
        """
        Migrate data from old organization collection to new one.
        
        Args:
            old_name: Old organization name
            new_name: New organization name
        """
        try:
            old_coll = self.db_manager.get_org_collection(old_name)
            new_coll = self.db_manager.get_org_collection(new_name)
            
            # Copy all documents
            # Note: For very large collections, this should be done in batches or using aggregation $out
            # For this assignment, simple copy is sufficient
            documents = list(old_coll.find())
            if documents:
                new_coll.insert_many(documents)
                
            # Drop old collection
            self.db_manager.drop_org_collection(old_name)
            logger.info(f"Migrated collection from {old_name} to {new_name}")
            
        except Exception as e:
            logger.error(f"Error migrating collection: {str(e)}")
            # In a real system, we might want to revert the name change here
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error migrating organization data"
            )
