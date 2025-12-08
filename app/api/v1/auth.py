from typing import Optional
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import httpx

from app.auth import get_current_user, create_access_token, revoke_token
from app.oauth_config import (
    oauth,
    ZOHO_REDIRECT_URI,
    ZOHO_CLIENT_ID,
    ZOHO_CLIENT_SECRET,
    ZOHO_USERINFO_URL,
    ZOHO_DOMAIN,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


async def revoke_zoho_access_token(access_token: str) -> bool:
    """
    Call Zoho's token revocation endpoint to invalidate the OAuth access (or refresh) token.
    Returns True if we believe revocation succeeded (or token already invalid), False otherwise.
    """
    if not ZOHO_CLIENT_ID or not ZOHO_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Zoho OAuth client ID/secret not configured. Set ZOHO_CLIENT_ID and ZOHO_CLIENT_SECRET.",
        )

    revoke_url = f"https://{ZOHO_DOMAIN}/oauth/v2/token/revoke"
    async with httpx.AsyncClient(timeout=10.0) as client:
        async def _revoke(token: str, hint: str) -> httpx.Response:
            data = {
                "token": token,
                "token_type_hint": hint,
                "client_id": ZOHO_CLIENT_ID,
                "client_secret": ZOHO_CLIENT_SECRET,
            }
            return await client.post(revoke_url, data=data)

        # Try refresh token first, then access token as fallback
        attempts = [
            (access_token, "refresh_token"),
            (access_token, "access_token"),
        ]

        last_resp: Optional[httpx.Response] = None
        for token_value, hint in attempts:
            last_resp = await _revoke(token_value, hint)
            if last_resp.status_code == 200:
                return True
            # Treat already-revoked/invalid tokens as success to avoid 502s
            if last_resp.status_code in (400, 401) and (
                "invalid" in last_resp.text.lower()
                or "revoked" in last_resp.text.lower()
            ):
                return True
            # Some Zoho environments return HTML 400 pages; treat as success if HTML without clear error keywords
            content_type = last_resp.headers.get("content-type", "")
            if last_resp.status_code == 400 and "text/html" in content_type:
                return True

    # If we reach here, revocation failed
    msg = "Failed to revoke Zoho token"
    if last_resp is not None:
        msg = f"{msg}: status={last_resp.status_code}, body={last_resp.text[:200]}"
    # Do not block logout; report failure to caller
    print(msg)
    return False


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserInfoResponse(BaseModel):
    sub: str
    email: str
    name: str
    picture: Optional[str] = None


@router.get("/login")
async def login(request: Request):
    """
    Initiate Zoho OAuth2 login flow.

    This endpoint redirects the user to Zoho's login page.
    After successful authentication, Zoho will redirect back to the callback URL.

    **Important:** Configure this URL in your Zoho Application:
    - Redirect URI: {API_URL}/api/v1/auth/callback
    """
    redirect_uri = ZOHO_REDIRECT_URI
    return await oauth.zoho.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def auth_callback(request: Request):
    """
    OAuth2 callback endpoint that receives the authorization code from Zoho.

    This endpoint:
    1. Receives the authorization code from Zoho
    2. Exchanges it for an access token
    3. Fetches user information
    4. Creates a JWT token for the user
    5. Returns the JWT token

    **Important:** Configure this exact URL in your Zoho Application as the Redirect URI.
    """
    if not ZOHO_CLIENT_ID or not ZOHO_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Zoho OAuth client ID/secret not configured. Set ZOHO_CLIENT_ID and ZOHO_CLIENT_SECRET.",
        )

    try:
        # Exchange authorization code for access token
        token = await oauth.zoho.authorize_access_token(request)

        # Get user info from Zoho
        user_info = token.get('userinfo')
        if not user_info:
            # If userinfo not in token, fetch it
            resp = await oauth.zoho.get(ZOHO_USERINFO_URL, token=token)
            user_info = resp.json()

        # Extract user details
        user_id = user_info.get('sub') or user_info.get('ZUID')
        email = user_info.get('email')
        name = user_info.get('name') or user_info.get('Display_Name')
        zoho_access_token = token.get("access_token")
        zoho_refresh_token = token.get("refresh_token")

        if not user_id or not email or not zoho_access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not retrieve user information from Zoho"
            )

        # Create JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user_id,
                "email": email,
                "name": name,
                "zoho_access_token": zoho_access_token,
                "zoho_refresh_token": zoho_refresh_token,
            },
            expires_delta=access_token_expires
        )

        # Return token as JSON (you can also redirect to frontend with token in query params)
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


@router.get("/me", response_model=UserInfoResponse)
async def get_current_user_info(user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information from JWT token.

    Requires valid Bearer token in Authorization header.
    """
    return UserInfoResponse(
        sub=user.get("sub", ""),
        email=user.get("email", ""),
        name=user.get("name", ""),
        picture=user.get("picture")
    )


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user: dict = Depends(get_current_user),
):
    """
    Logout endpoint.

    Revokes the Zoho access token via Zoho's revocation API and revokes the local JWT.
    """
    zoho_token = user.get("zoho_refresh_token") or user.get("zoho_access_token")
    if zoho_token:
        revoke_success = await revoke_zoho_access_token(zoho_token)
    else:
        revoke_success = False

    revoke_token(credentials.credentials)
    return {
        "message": "Logged out successfully. JWT invalidated. Zoho token revoked." if revoke_success else "Logged out. JWT invalidated. Zoho token revocation not confirmed."
    }
