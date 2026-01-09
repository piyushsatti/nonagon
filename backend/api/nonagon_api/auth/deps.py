"""
FastAPI dependencies for authentication.
"""

from typing import Optional, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .jwt import decode_token
from .models import AuthenticatedUser


# Security scheme for Swagger UI
security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)]
) -> Optional[AuthenticatedUser]:
    """
    Get the current authenticated user if a valid token is provided.
    
    Returns None if no token is provided or if the token is invalid.
    Use this for endpoints that work with or without authentication.
    """
    if credentials is None:
        return None
    
    user = decode_token(credentials.credentials)
    return user


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)]
) -> AuthenticatedUser:
    """
    Get the current authenticated user, requiring valid authentication.
    
    Raises HTTPException 401 if no token is provided or if the token is invalid.
    Use this for endpoints that require authentication.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = decode_token(credentials.credentials)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user
