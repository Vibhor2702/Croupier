"""
Repository layer for organization data access.
Handles all database operations for organizations.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from app.db import DatabaseManager
import logging

logger = logging.getLogger(__name__)


class OrganizationRepository:
    """Repository for organization CRUD operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize repository with database manager.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.collection = db_manager.organizations
    
    def create(self, organization_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new organization.
        
        Args:
            organization_data: Dictionary containing organization details
            
        Returns:
            Created organization document with _id converted to string
            
        Raises:
            DuplicateKeyError: If organization name already exists
        """
        try:
            organization_data['created_at'] = datetime.utcnow()
            organization_data['updated_at'] = None
            
            result = self.collection.insert_one(organization_data)
            organization_data['_id'] = result.inserted_id
            
            logger.info(f"Created organization: {organization_data['organization_name']}")
            return self._serialize_document(organization_data)
        except DuplicateKeyError:
            logger.error(f"Organization already exists: {organization_data['organization_name']}")
            raise
    
    def find_by_name(self, organization_name: str) -> Optional[Dict[str, Any]]:
        """
        Find organization by name.
        
        Args:
            organization_name: Name of the organization
            
        Returns:
            Organization document or None if not found
        """
        doc = self.collection.find_one({"organization_name": organization_name})
        if doc:
            return self._serialize_document(doc)
        return None
    
    def find_by_id(self, organization_id: str) -> Optional[Dict[str, Any]]:
        """
        Find organization by ID.
        
        Args:
            organization_id: MongoDB ObjectId as string
            
        Returns:
            Organization document or None if not found
        """
        try:
            doc = self.collection.find_one({"_id": ObjectId(organization_id)})
            if doc:
                return self._serialize_document(doc)
        except Exception as e:
            logger.error(f"Error finding organization by ID: {str(e)}")
        return None
    
    def update(
        self,
        organization_name: str,
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update organization details.
        
        Args:
            organization_name: Current organization name
            update_data: Dictionary of fields to update
            
        Returns:
            Updated organization document or None if not found
        """
        update_data['updated_at'] = datetime.utcnow()
        
        result = self.collection.find_one_and_update(
            {"organization_name": organization_name},
            {"$set": update_data},
            return_document=True
        )
        
        if result:
            logger.info(f"Updated organization: {organization_name}")
            return self._serialize_document(result)
        return None
    
    def delete(self, organization_name: str) -> bool:
        """
        Delete an organization.
        
        Args:
            organization_name: Name of the organization to delete
            
        Returns:
            True if deleted, False if not found
        """
        result = self.collection.delete_one({"organization_name": organization_name})
        
        if result.deleted_count > 0:
            logger.info(f"Deleted organization: {organization_name}")
            return True
        return False
    
    def exists(self, organization_name: str) -> bool:
        """
        Check if organization exists.
        
        Args:
            organization_name: Name to check
            
        Returns:
            True if exists, False otherwise
        """
        return self.collection.count_documents(
            {"organization_name": organization_name}
        ) > 0
    
    @staticmethod
    def _serialize_document(doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert MongoDB document to JSON-serializable format.
        
        Args:
            doc: MongoDB document
            
        Returns:
            Serialized document with _id as string
        """
        if '_id' in doc and isinstance(doc['_id'], ObjectId):
            doc['id'] = str(doc['_id'])
            del doc['_id']
        return doc
