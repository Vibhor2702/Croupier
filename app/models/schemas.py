"""
Pydantic models for request validation and response serialization.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re


class OrganizationCreate(BaseModel):
    """Schema for creating a new organization."""
    organization_name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @validator('organization_name')
    def validate_organization_name(cls, v):
        """Validate organization name format (alphanumeric, underscores, hyphens)."""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError(
                'Organization name must contain only alphanumeric characters, '
                'underscores, and hyphens'
            )
        return v.lower()  # Normalize to lowercase
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password complexity."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization."""
    organization_name: Optional[str] = Field(None, min_length=3, max_length=50, description="New organization name")
    email: Optional[EmailStr] = Field(None, description="New admin email")
    password: Optional[str] = Field(None, min_length=8, description="New admin password")
    
    @validator('organization_name')
    def validate_organization_name(cls, v):
        """Validate organization name format."""
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9_-]+$', v):
                raise ValueError(
                    'Organization name must contain only alphanumeric characters, '
                    'underscores, and hyphens'
                )
            return v.lower()
        return v
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password complexity."""
        if v is not None:
            if len(v) < 8:
                raise ValueError('Password must be at least 8 characters long')
            if not any(c.isupper() for c in v):
                raise ValueError('Password must contain at least one uppercase letter')
            if not any(c.islower() for c in v):
                raise ValueError('Password must contain at least one lowercase letter')
            if not any(c.isdigit() for c in v):
                raise ValueError('Password must contain at least one digit')
        return v


class OrganizationGet(BaseModel):
    """Schema for retrieving organization details."""
    organization_name: str


class OrganizationDelete(BaseModel):
    """Schema for deleting an organization."""
    organization_name: str


class OrganizationResponse(BaseModel):
    """Schema for organization response."""
    id: str
    organization_name: str
    email: EmailStr
    connection_details: Optional[str] = Field(None, description="Connection details for organization's dynamic database")
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AdminLogin(BaseModel):
    """Schema for admin login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    admin_id: str
    organization_id: str
    organization_name: str


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str
