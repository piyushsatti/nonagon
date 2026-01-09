"""
OAuth2 routes for Discord authentication.
"""

import os
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse

from .models import AuthenticatedUser, DiscordUserResponse, TokenResponse
from .jwt import create_access_token


router = APIRouter(prefix="/auth", tags=["authentication"])

# Discord OAuth2 configuration
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID", "")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET", "")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI", "http://localhost:8000/auth/discord/callback")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:1234")

DISCORD_API_ENDPOINT = "https://discord.com/api/v10"
DISCORD_OAUTH_AUTHORIZE_URL = "https://discord.com/api/oauth2/authorize"
DISCORD_OAUTH_TOKEN_URL = "https://discord.com/api/oauth2/token"


@router.get("/discord/login")
async def discord_login():
    """
    Initiate Discord OAuth2 login flow.
    
    Redirects the user to Discord's authorization page.
    """
    if not DISCORD_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Discord OAuth is not configured",
        )
    
    params = {
        "client_id": DISCORD_CLIENT_ID,
        "redirect_uri": DISCORD_REDIRECT_URI,
        "response_type": "code",
        "scope": "identify",
    }
    
    authorization_url = f"{DISCORD_OAUTH_AUTHORIZE_URL}?{urlencode(params)}"
    return RedirectResponse(url=authorization_url)


@router.get("/discord/callback")
async def discord_callback(code: str):
    """
    Handle Discord OAuth2 callback.
    
    Exchanges the authorization code for an access token,
    fetches user info, and redirects to frontend with JWT.
    """
    if not DISCORD_CLIENT_ID or not DISCORD_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Discord OAuth is not configured",
        )
    
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            DISCORD_OAUTH_TOKEN_URL,
            data={
                "client_id": DISCORD_CLIENT_ID,
                "client_secret": DISCORD_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": DISCORD_REDIRECT_URI,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange code for token",
            )
        
        token_data = token_response.json()
        discord_access_token = token_data.get("access_token")
        
        # Fetch user info from Discord
        user_response = await client.get(
            f"{DISCORD_API_ENDPOINT}/users/@me",
            headers={"Authorization": f"Bearer {discord_access_token}"},
        )
        
        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch user info from Discord",
            )
        
        discord_user = DiscordUserResponse(**user_response.json())
    
    # Create our authenticated user
    user = AuthenticatedUser(
        user_id=discord_user.id,
        username=discord_user.global_name or discord_user.username,
        discriminator=discord_user.discriminator,
        avatar=discord_user.avatar,
    )
    
    # Generate JWT
    access_token = create_access_token(user)
    
    # Redirect to frontend with token in URL fragment (for client-side handling)
    redirect_url = f"{FRONTEND_URL}/login?token={access_token}&userId={user.user_id}&username={user.username}"
    return RedirectResponse(url=redirect_url)


@router.get("/me", response_model=AuthenticatedUser)
async def get_current_user_info(
    user: AuthenticatedUser = None,
):
    """
    Get information about the currently authenticated user.
    
    This endpoint requires authentication.
    """
    # Note: This would normally use Depends(get_current_user)
    # but we want to avoid circular imports. The main.py will
    # add proper dependency injection.
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user


@router.post("/logout")
async def logout():
    """
    Logout endpoint.
    
    Since we use JWTs, actual logout happens client-side by
    removing the token. This endpoint is provided for completeness.
    """
    return {"message": "Logged out successfully"}
