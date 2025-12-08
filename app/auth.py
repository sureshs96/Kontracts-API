from datetime import datetime, timedelta
from typing import Optional, Set
import uuid
import hashlib
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.oauth_config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Security scheme for Swagger UI
security = HTTPBearer()
revoked_jtis: Set[str] = set()
revoked_token_digests: Set[str] = set()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token.

    Args:
        data: Dictionary containing the claims to encode in the token
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    to_encode.setdefault("jti", uuid.uuid4().hex)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Check explicit token hash blacklist for tokens issued without jti
        token_digest = hashlib.sha256(token.encode()).hexdigest()
        if token_digest in revoked_token_digests:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
        jti = payload.get("jti")
        if jti and jti in revoked_jtis:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to get the current authenticated user from JWT token.
    Requires a valid Bearer token in the Authorization header.

    Usage:
        @router.get("/protected")
        async def protected_route(user: dict = Depends(get_current_user)):
            user_id = user.get("sub")
            return {"user_id": user_id}
    """
    token = credentials.credentials
    payload = verify_token(token)

    if payload.get("sub") is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def revoke_token(token: str) -> None:
    """
    Revoke a JWT by recording its jti.

    Note: This is in-memory only. Use a shared store (e.g., Redis) for multi-instance deployments.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        # If token can't be decoded, nothing to revoke
        return

    jti = payload.get("jti")
    if jti:
        revoked_jtis.add(jti)
    else:
        revoked_token_digests.add(hashlib.sha256(token.encode()).hexdigest())


async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))):
    """
    Dependency to get the current user if authenticated, otherwise None.
    Does not require authentication but provides user info if available.

    Usage:
        @router.get("/optional-auth")
        async def optional_route(user: Optional[dict] = Depends(get_optional_user)):
            if user:
                user_id = user.get("sub")
                return {"user_id": user_id, "authenticated": True}
            return {"authenticated": False}
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        payload = verify_token(token)
        return payload
    except HTTPException:
        return None


def get_user_id(user: dict) -> str:
    """
    Helper function to extract user_id from decoded token payload.

    Usage:
        user_id = get_user_id(user)
    """
    return user.get("sub", "")
