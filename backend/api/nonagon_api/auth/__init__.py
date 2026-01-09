"""
Authentication module for Nonagon API.

Provides Discord OAuth2 authentication and JWT-based session management.
"""

from .models import AuthenticatedUser, TokenPayload, TokenResponse
from .jwt import create_access_token, decode_token
from .deps import get_current_user, get_current_user_optional
from .router import router as auth_router

__all__ = [
    "AuthenticatedUser",
    "TokenPayload",
    "TokenResponse",
    "create_access_token",
    "decode_token",
    "get_current_user",
    "get_current_user_optional",
    "auth_router",
]
