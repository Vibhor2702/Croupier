"""
Database connection and initialization module.
Manages MongoDB connections for master database and dynamic organization collections.
"""
from pymongo import MongoClient, ASCENDING
from pymongo.database import Database
from pymongo.collection import Collection
from typing import Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Singleton database manager for MongoDB connections."""
    
    _instance: Optional['DatabaseManager'] = None
    _client: Optional[MongoClient] = None
    _master_db: Optional[Database] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def connect(self) -> None:
        """Establish connection to MongoDB."""
        if self._client is None:
            self._client = MongoClient(settings.MONGODB_URL)
            self._master_db = self._client[settings.MONGODB_DB_NAME]
            self._initialize_master_db()
            logger.info(f"Connected to MongoDB: {settings.MONGODB_URL}")
    
    def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._master_db = None
            logger.info("Disconnected from MongoDB")
    
    def _initialize_master_db(self) -> None:
        """Initialize master database with required collections and indexes."""
        # Create indexes for organizations collection
        self.master_db.organizations.create_index(
            [("organization_name", ASCENDING)], 
            unique=True
        )
        
        # Create indexes for admin_users collection
        self.master_db.admin_users.create_index(
            [("email", ASCENDING)], 
            unique=True
        )
        self.master_db.admin_users.create_index(
            [("organization_id", ASCENDING)]
        )
        
        logger.info("Master database initialized with indexes")
    
    @property
    def master_db(self) -> Database:
        """Get master database instance."""
        if self._master_db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._master_db
    
    @property
    def organizations(self) -> Collection:
        """Get organizations collection from master database."""
        return self.master_db.organizations
    
    @property
    def admin_users(self) -> Collection:
        """Get admin_users collection from master database."""
        return self.master_db.admin_users
    
    def get_org_collection(self, organization_name: str) -> Collection:
        """
        Get or create a dynamic collection for an organization.
        
        Args:
            organization_name: Name of the organization
            
        Returns:
            Collection instance for the organization
        """
        collection_name = f"org_{organization_name}"
        return self.master_db[collection_name]
    
    def drop_org_collection(self, organization_name: str) -> None:
        """
        Drop an organization's dynamic collection.
        
        Args:
            organization_name: Name of the organization
        """
        collection_name = f"org_{organization_name}"
        self.master_db.drop_collection(collection_name)
        logger.info(f"Dropped collection: {collection_name}")


# Global database manager instance
db_manager = DatabaseManager()


def get_db() -> DatabaseManager:
    """Dependency injection function for FastAPI routes."""
    return db_manager
