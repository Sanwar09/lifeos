"""
LifeOS AI — Google OAuth2 Authentication Module
Handles secure OAuth2 login, state validation, account provisioning, session cookies, and logout.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Response, Status, Request, Cookie
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


async def get_current_user_optional(
    request: Request,
    access_token: str | None = Cookie(None),
    db: AsyncSession = Depends(get_db)
) -> User | None:
    """Helper to retrieve current user from cookie or bearer token if present."""
    token = access_token
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
    if not token:
        return None
        
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if not email:
            return None
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()
    except Exception:
        return None


@router.get("/google/login", summary="Initiate Google OAuth2 Login Flow")
async def google_login(response: Response):
    """
    Generates a cryptographically secure CSRF state token, stores it in a secure HttpOnly cookie,
    and redirects the user to Google's OAuth2 consent screen.
    """
    if not settings.google_client_id:
        logger.warning("Google Client ID is not configured. Redirecting with simulation mode or error.")
        raise HTTPException(
            status_code=503,
            detail="Google OAuth2 is not configured on this server. Please set GOOGLE_CLIENT_ID in environment."
        )

    state = secrets.token_urlsafe(32)
    
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=600
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

    return RedirectResponse(url=google_auth_url, status_code=303)


@router.get("/google/callback", summary="Handle Google OAuth2 Callback & User Provisioning")
async def google_callback(
    response: Response,
    code: str = Query(...),
    state: str = Query(...),
    oauth_state: str | None = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Handles the Google OAuth2 callback, CSRF validation, token exchange, and user provisioning.
    """
    if not oauth_state or state != oauth_state:
        logger.error("OAuth CSRF state mismatch or missing state cookie.")
        return RedirectResponse(url="/?error=auth_failed_state_mismatch", status_code=303)

    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "code": code,
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "redirect_uri": settings.google_redirect_uri,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        token_res = await client.post(token_url, data=payload)
        if token_res.status_code != 200:
            logger.error("Failed to exchange Google auth code: %s", token_res.text)
            return RedirectResponse(url="/?error=token_exchange_failed", status_code=303)
        
        token_data = token_res.json()
        id_token_str = token_data.get("id_token")
        
        if not id_token_str:
            return RedirectResponse(url="/?error=missing_id_token", status_code=303)

        try:
            # Decode Google ID token (unverified or verified via google API)
            # For robustness, fetch user info via userinfo endpoint
            userinfo_res = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {token_data.get('access_token')}"}
            )
            if userinfo_res.status_code != 200:
                return RedirectResponse(url="/?error=userinfo_failed", status_code=303)
            
            user_info = userinfo_res.json()
            email = user_info.get("email")
            name = user_info.get("name", email.split("@")[0] if email else "User")
            picture = user_info.get("picture")

            if not email:
                return RedirectResponse(url="/?error=email_not_provided", status_code=303)

            # Provision or update user in database
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalars().first()

            if not user:
                user = User(
                    email=email,
                    name=name,
                    avatar_url=picture,
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.add(user)
            else:
                user.name = name
                user.avatar_url = picture
                user.last_login = datetime.utcnow()
            
            await db.commit()

            # Issue JWT access token cookie
            access_token = create_access_token(data={"sub": email, "name": name})
            
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=settings.environment == "production",
                samesite="lax",
                max_age=settings.access_token_expire_minutes * 60
            )

            return RedirectResponse(url="/dashboard.html", status_code=303)

        except Exception as e:
            logger.exception("Error during Google OAuth callback processing: %s", str(e))
            return RedirectResponse(url="/?error=internal_auth_error", status_code=303)


@router.post("/logout", summary="Log out user and clear session cookie")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"status": "logged_out"}