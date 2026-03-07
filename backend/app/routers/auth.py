"""Google OAuth authentication endpoints."""

import json

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from google_auth_oauthlib.flow import Flow
from pydantic import BaseModel

from app.core.config import settings
from app.core.session import (
    User,
    create_user_id,
    set_session_cookie,
    clear_session_cookie,
    get_current_user,
    get_current_user_optional,
    get_user_token_path,
)

router = APIRouter()

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]


class AuthStatus(BaseModel):
    """Authentication status."""

    authenticated: bool
    user: User | None = None
    google_drive_connected: bool = False


class GoogleAuthUrl(BaseModel):
    """OAuth URL response."""

    url: str


def get_redirect_uri(request: Request) -> str:
    """Build the OAuth callback URL based on the incoming request."""
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("x-forwarded-host", request.url.netloc)
    return f"{scheme}://{host}/api/auth/google/callback"


def create_flow(request: Request) -> Flow:
    """Create OAuth flow from settings."""
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=400,
            detail="Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.",
        )

    client_config = {
        "web": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [get_redirect_uri(request)],
        }
    }

    flow = Flow.from_client_config(client_config, scopes=SCOPES)
    flow.redirect_uri = get_redirect_uri(request)
    return flow


@router.get("/auth/status", response_model=AuthStatus)
async def auth_status(user: User | None = Depends(get_current_user_optional)):
    """Get current authentication status."""
    if not user:
        return AuthStatus(authenticated=False)

    # Check if Google Drive token exists for this user
    token_path = get_user_token_path(user.id)
    drive_connected = token_path.exists()

    return AuthStatus(
        authenticated=True,
        user=user,
        google_drive_connected=drive_connected,
    )


@router.get("/auth/login")
async def login_url(request: Request, force_consent: bool = False):
    """Get the Google OAuth URL for login.

    Args:
        force_consent: If True, force the consent screen (needed for Drive reconnection).
    """
    flow = create_flow(request)

    # Use 'consent' when reconnecting Drive to ensure we get a refresh token
    # Use 'select_account' for regular login to skip consent if already granted
    prompt_type = "consent" if force_consent else "select_account"

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt=prompt_type,
    )

    # Store code_verifier in a signed cookie so callback can complete PKCE exchange
    from itsdangerous import URLSafeTimedSerializer

    s = URLSafeTimedSerializer(settings.session_secret)
    verifier_token = s.dumps({"cv": flow.code_verifier, "state": state})

    response = JSONResponse(content={"url": authorization_url})
    response.set_cookie(
        "oauth_verifier",
        verifier_token,
        max_age=600,
        httponly=True,
        samesite="lax",
        secure=True,
    )
    return response


@router.get("/auth/google/callback")
async def google_auth_callback(
    request: Request, code: str | None = None, error: str | None = None
):
    """Handle OAuth callback from Google."""
    if error:
        return RedirectResponse(url=f"/?auth_error={error}")

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    try:
        flow = create_flow(request)

        # Restore PKCE code_verifier from signed cookie
        verifier_token = request.cookies.get("oauth_verifier")
        if verifier_token:
            from itsdangerous import URLSafeTimedSerializer

            s = URLSafeTimedSerializer(settings.session_secret)
            data = s.loads(verifier_token, max_age=600)
            flow.code_verifier = data.get("cv")

        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Get user info from Google
        from googleapiclient.discovery import build

        service = build("oauth2", "v2", credentials=credentials)
        user_info = service.userinfo().get().execute()

        email = user_info.get("email", "").lower()
        google_id = user_info.get("id")
        name = user_info.get("name")
        picture = user_info.get("picture")

        # Check if user is in allowlist
        allowed_users = settings.get_allowed_users_list()
        if allowed_users and email not in allowed_users:
            return RedirectResponse(url="/?auth_error=access_denied")

        # Create user
        user_id = create_user_id(google_id)
        user = User(
            id=user_id,
            email=email,
            name=name,
            picture=picture,
        )

        # Save Google token for this user (for Drive access)
        token_path = get_user_token_path(user_id)
        token_path.parent.mkdir(parents=True, exist_ok=True)

        token_data = json.loads(credentials.to_json())
        token_data["email"] = email
        token_path.write_text(json.dumps(token_data, indent=2))

        # Create session and redirect
        response = RedirectResponse(url="/?auth_success=true")
        set_session_cookie(response, user)
        response.delete_cookie("oauth_verifier")
        return response

    except Exception as e:
        print(f"Auth error: {e}")
        return RedirectResponse(url=f"/?auth_error={str(e)}")


@router.post("/auth/logout")
async def logout():
    """Log out the current user."""
    response = JSONResponse(content={"message": "Logged out"})
    clear_session_cookie(response)
    return response


@router.delete("/auth/google/disconnect")
async def google_disconnect(user: User = Depends(get_current_user)):
    """Disconnect Google Drive (revoke token) for the current user."""
    token_path = get_user_token_path(user.id)

    if not token_path.exists():
        return {"message": "Not connected"}

    try:
        # Try to revoke the token
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        if creds.token:
            import httpx

            httpx.post(
                "https://oauth2.googleapis.com/revoke",
                params={"token": creds.token},
                headers={"content-type": "application/x-www-form-urlencoded"},
            )
    except Exception:
        pass  # Best effort revocation

    # Remove local token
    token_path.unlink(missing_ok=True)

    return {"message": "Disconnected"}


# Legacy endpoints for backward compatibility
@router.get("/auth/google/status")
async def google_auth_status_legacy(
    user: User | None = Depends(get_current_user_optional),
):
    """Legacy endpoint - check if Google Drive is connected."""
    if not user:
        return {"connected": False, "email": None}

    token_path = get_user_token_path(user.id)
    if not token_path.exists():
        return {"connected": False, "email": None}

    try:
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        if creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
            token_path.write_text(creds.to_json())

        if creds.valid:
            token_data = json.loads(token_path.read_text())
            return {"connected": True, "email": token_data.get("email")}
    except Exception:
        token_path.unlink(missing_ok=True)

    return {"connected": False, "email": None}


@router.get("/auth/google/url")
async def google_auth_url_legacy(request: Request):
    """Legacy endpoint - get OAuth URL for Drive connection (forces consent)."""
    return await login_url(request, force_consent=True)
