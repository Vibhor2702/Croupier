"""
JWT token generation and validation utilities.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class JWTHandler:
    """Handler for JWT token operations."""
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a new JWT access token.
        
        Args:
            data: Payload data to encode in the token
            expires_delta: Optional custom expiration time
            
        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow()
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        logger.info(f"Created JWT token for data: {data.get('sub', 'unknown')}")
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string to verify
            
        Returns:
            Decoded token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError as e:
            logger.error(f"JWT verification failed: {str(e)}")
            return None
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        Decode a JWT token without verification (for debugging).
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
        """
        try:
            return jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_signature": False}
            )
        except JWTError as e:
            logger.error(f"JWT decoding failed: {str(e)}")
            return {}


# Singleton instance
jwt_handler = JWTHandler()
