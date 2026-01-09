"""
JWT token creation and verification utilities.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt

from .models import TokenPayload, AuthenticatedUser


# Configuration from environment
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))


def create_access_token(user: AuthenticatedUser, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token for the authenticated user.
    
    Args:
        user: The authenticated user to create a token for
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    payload = TokenPayload(
        sub=user.user_id,
        username=user.username,
        discriminator=user.discriminator,
        avatar=user.avatar,
        exp=int(expire.timestamp()),
    )
    
    encoded_jwt = jwt.encode(
        payload.model_dump(),
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )
    
    return encoded_jwt


def decode_token(token: str) -> Optional[AuthenticatedUser]:
    """
    Decode and verify a JWT token.
    
    Args:
        token: The JWT token string to decode
        
    Returns:
        AuthenticatedUser if valid, None if invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        
        user_id = payload.get("sub")
        if user_id is None:
            return None
        
        return AuthenticatedUser(
            user_id=user_id,
            username=payload.get("username", "Unknown"),
            discriminator=payload.get("discriminator"),
            avatar=payload.get("avatar"),
        )
    except JWTError:
        return None
