"""
Repository layer for admin user data access.
Handles all database operations for admin users.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from app.db import DatabaseManager
import logging

logger = logging.getLogger(__name__)


class AdminRepository:
    """Repository for admin user CRUD operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize repository with database manager.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.collection = db_manager.admin_users
    
    def create(self, admin_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new admin user.
        
        Args:
            admin_data: Dictionary containing admin user details
            
        Returns:
            Created admin document with _id converted to string
            
        Raises:
            DuplicateKeyError: If email already exists
        """
        try:
            admin_data['created_at'] = datetime.utcnow()
            admin_data['updated_at'] = None
            
            result = self.collection.insert_one(admin_data)
            admin_data['_id'] = result.inserted_id
            
            logger.info(f"Created admin user: {admin_data['email']}")
            return self._serialize_document(admin_data)
        except DuplicateKeyError:
            logger.error(f"Admin email already exists: {admin_data['email']}")
            raise
    
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find admin user by email.
        
        Args:
            email: Email address of the admin
            
        Returns:
            Admin document or None if not found
        """
        doc = self.collection.find_one({"email": email})
        if doc:
            return self._serialize_document(doc)
        return None
    
    def find_by_id(self, admin_id: str) -> Optional[Dict[str, Any]]:
        """
        Find admin user by ID.
        
        Args:
            admin_id: MongoDB ObjectId as string
            
        Returns:
            Admin document or None if not found
        """
        try:
            doc = self.collection.find_one({"_id": ObjectId(admin_id)})
            if doc:
                return self._serialize_document(doc)
        except Exception as e:
            logger.error(f"Error finding admin by ID: {str(e)}")
        return None
    
    def find_by_organization(self, organization_id: str) -> Optional[Dict[str, Any]]:
        """
        Find admin user by organization ID.
        
        Args:
            organization_id: Organization's MongoDB ObjectId as string
            
        Returns:
            Admin document or None if not found
        """
        doc = self.collection.find_one({"organization_id": organization_id})
        if doc:
            return self._serialize_document(doc)
        return None
    
    def update(
        self,
        admin_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update admin user details.
        
        Args:
            admin_id: Admin user's MongoDB ObjectId as string
            update_data: Dictionary of fields to update
            
        Returns:
            Updated admin document or None if not found
        """
        update_data['updated_at'] = datetime.utcnow()
        
        try:
            result = self.collection.find_one_and_update(
                {"_id": ObjectId(admin_id)},
                {"$set": update_data},
                return_document=True
            )
            
            if result:
                logger.info(f"Updated admin user: {admin_id}")
                return self._serialize_document(result)
        except Exception as e:
            logger.error(f"Error updating admin: {str(e)}")
        return None
    
    def delete_by_organization(self, organization_id: str) -> bool:
        """
        Delete admin user by organization ID.
        
        Args:
            organization_id: Organization's MongoDB ObjectId as string
            
        Returns:
            True if deleted, False if not found
        """
        result = self.collection.delete_one({"organization_id": organization_id})
        
        if result.deleted_count > 0:
            logger.info(f"Deleted admin user for organization: {organization_id}")
            return True
        return False
    
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
