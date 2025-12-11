"""
Configuration module for Croupier application.
Loads environment variables and provides application settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Croupier"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # MongoDB Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "croupier_master"
    
    # JWT Configuration
    JWT_SECRET_KEY: str = "your-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Security
    BCRYPT_ROUNDS: int = 12
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
