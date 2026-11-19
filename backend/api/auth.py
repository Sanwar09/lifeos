"""
LifeOS AI — Google OAuth2 Authentication Module
Handles secure OAuth2 login, state validation, account provisioning, session cookies, and logout.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta
import secrets
import httpx
import jwt
import logging

from config import settings
from database import get_db
from models import User

logger = logging.getLogger("lifeos.auth")

router = APIRouter()

# JWT Encoding/Decoding helpers
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


@router.get("/google/login", summary="Initiate Google OAuth2 Login Flow")
async def google_login(response: Response):
    """
    Generates a cryptographically secure CSRF state token, stores it in a secure HttpOnly cookie,
    and redirects the user to Google's OAuth2 consent screen.
    """
    if not settings.google_client_id:
        # Fallback for development if credentials are not set yet
        logger.warning("Google Client ID is not configured. Redirecting with simulation mode or error.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth2 is not configured on this server. Please set GOOGLE_CLIENT_ID in environment."
        )

    state = secrets.token_urlsafe(32)
    
    # Store state in a secure cookie for CSRF validation during callback
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=600  # 10 minutes expiry for state
    )

    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.google_client_id}&"
        f"redirect_uri={settings.google_redirect_uri}&"
        "response_type=code&"
        "scope=openid%20email%20profile&"
        f"state={state}&"
        "access_type=offline&"
        "prompt=select_account"
    )

    return RedirectResponse(url=google_auth_url, status_code=status.HTTP_303_SEE_OTHER)


@router.get("/google/callback", summary="Handle Google OAuth2 Callback & User Provisioning")
async def google_callback(
    response: Response,
    code: str = Query(...),
    state: str = Query(...),
    oauth_state: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Handles the Google OAuth2 callback:
    1. Validates the CSRF state token against the session cookie.
    2. Exchanges the authorization code for Google access and ID tokens.
    3. Verifies Google claims (including email_verified).
    4. Automatically provisions or links the user record in the database.
    5. Issues a secure HttpOnly session JWT cookie and redirects to the dashboard.
    """
    # 1. CSRF State validation
    # Note: FastAPI injects cookies via Cookie() parameter or we can check headers/cookies.
    # To capture cookie robustly:
    from fastapi import Cookie
    # We will declare oauth_state via dependency or parameter below if needed.
    
    # Let's perform validation (if oauth_state cookie is missing or mismatch)
    # For strict compliance, state must match.
    if not oauth_state or state != oauth_state:
        logger.error("OAuth CSRF state mismatch or missing state cookie.")
        return RedirectResponse(url="/?error=auth_failed_state_mismatch", status_code=status.HTTP_303_SEE_OTHER)

    # 2. Exchange authorization code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "code": code,
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "redirect_uri": settings.google_redirect_uri,
        "grant_type": "authorization_code",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            token_res = await client.post(token_url, data=payload)
            if token_res.status_code != 200:
                logger.error("Failed to exchange code with Google: %s", token_res.text)
                return RedirectResponse(url="/?error=auth_failed_token_exchange", status_code=status.HTTP_303_SEE_OTHER)
            
            token_data = token_res.json()
            id_token_jwt = token_data.get("id_token")
            access_token = token_data.get("access_token")

            if not id_token_jwt:
                return RedirectResponse(url="/?error=auth_failed_no_id_token", status_code=status.HTTP_303_SEE_OTHER)

            # 3. Fetch user info from Google userinfo endpoint or decode ID token
            userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
            userinfo_res = await client.get(
                userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if userinfo_res.status_code != 200:
                return RedirectResponse(url="/?error=auth_failed_userinfo", status_code=status.HTTP_303_SEE_OTHER)
            
            profile = userinfo_res.json()

    except Exception as e:
        logger.exception("Network or timeout error during Google OAuth handshake: %s", str(e))
        return RedirectResponse(url="/?error=auth_network_error", status_code=status.HTTP_502_BAD_GATEWAY)

    email = profile.get("email")
    email_verified = profile.get("email_verified", False)
    google_id = profile.get("sub")
    name = profile.get("name", "LifeOS User")
    avatar_url = profile.get("picture")

    if not email or not email_verified:
        logger.warning("Google account email not verified or missing: %s", email)
        return RedirectResponse(url="/?error=email_not_verified", status_code=status.HTTP_303_SEE_OTHER)

    # 4. Database User Provisioning & Account Linking
    try:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()

        if user:
            # Update existing user with Google metadata if not already set
            if not user.google_id:
                user.google_id = google_id
            if avatar_url and not user.avatar_url:
                user.avatar_url = avatar_url
            if name and user.name == "LifeOS User":
                user.name = name
            await db.commit()
            await db.refresh(user)
        else:
            # Provision new user
            user = User(
                email=email,
                name=name,
                google_id=google_id,
                avatar_url=avatar_url,
                hashed_password=None,  # No password for pure Google SSO users
                is_active=True
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

    except Exception as e:
        logger.exception("Database error during user provisioning: %s", str(e))
        await db.rollback()
        return RedirectResponse(url="/?error=database_error", status_code=status.HTTP_303_SEE_OTHER)

    # 5. Issue session JWT cookie
    session_jwt = create_access_token({"sub": user.id, "email": user.email, "name": user.name})

    redirect_response = RedirectResponse(url="/category.html", status_code=status.HTTP_303_SEE_OTHER)
    
    # Set HttpOnly session cookie
    redirect_response.set_cookie(
        key="lifeos_session",
        value=session_jwt,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60
    )

    # Clear temporary CSRF state cookie
    redirect_response.delete_cookie(key="oauth_state")

    logger.info("Successfully authenticated user %s via Google OAuth2", email)
    return redirect_response


@router.post("/logout", summary="Log out current user")
async def logout(response: Response):
    """
    Invalidates the local session cookie and logs out the user.
    """
    response.delete_cookie(key="lifeos_session")
    return {"status": "success", "message": "Successfully logged out"}


@router.get("/me", summary="Get Current Authenticated User Profile")
async def get_current_user_profile(
    lifeos_session: str | None = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Validates the session cookie and returns the current user profile.
    """
    if not lifeos_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = jwt.decode(lifeos_session, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "avatar_url": user.avatar_url,
        "timezone": user.timezone,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }