"""
Pydantic models for authentication.
"""

from pydantic import BaseModel
from typing import Optional


class TokenPayload(BaseModel):
    """JWT token payload structure."""
    
    sub: str  # User ID
    username: str
    discriminator: Optional[str] = None
    avatar: Optional[str] = None
    exp: Optional[int] = None


class AuthenticatedUser(BaseModel):
    """Represents an authenticated user in the system."""
    
    user_id: str
    username: str
    discriminator: Optional[str] = None
    avatar: Optional[str] = None
    
    @property
    def avatar_url(self) -> Optional[str]:
        """Get the full Discord avatar URL."""
        if not self.avatar:
            return None
        return f"https://cdn.discordapp.com/avatars/{self.user_id}/{self.avatar}.png"


class TokenResponse(BaseModel):
    """Response returned after successful authentication."""
    
    access_token: str
    token_type: str = "bearer"
    user: AuthenticatedUser


class DiscordUserResponse(BaseModel):
    """Response from Discord's /users/@me endpoint."""
    
    id: str
    username: str
    discriminator: str
    avatar: Optional[str] = None
    global_name: Optional[str] = None
