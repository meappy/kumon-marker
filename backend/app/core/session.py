"""Session management for user authentication."""

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from fastapi import Cookie, HTTPException, Request, Response
from pydantic import BaseModel
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from app.core.config import settings


SESSION_COOKIE_NAME = "kumon_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 30  # 30 days


class User(BaseModel):
    """Authenticated user."""
    id: str  # Hashed Google ID
    email: str
    name: str | None = None
    picture: str | None = None


def get_serializer() -> URLSafeTimedSerializer:
    """Get the session serializer."""
    return URLSafeTimedSerializer(settings.session_secret)


def create_user_id(google_id: str) -> str:
    """Create a stable user ID from Google ID."""
    return hashlib.sha256(google_id.encode()).hexdigest()[:16]


def create_session_token(user: User) -> str:
    """Create a signed session token for a user."""
    serializer = get_serializer()
    return serializer.dumps({
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "picture": user.picture,
    })


def decode_session_token(token: str) -> Optional[User]:
    """Decode and validate a session token."""
    serializer = get_serializer()
    try:
        data = serializer.loads(token, max_age=SESSION_MAX_AGE)
        return User(**data)
    except (BadSignature, SignatureExpired):
        return None


def set_session_cookie(response: Response, user: User) -> None:
    """Set the session cookie on a response."""
    token = create_session_token(user)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=False,  # Set to True in production with HTTPS
    )


def clear_session_cookie(response: Response) -> None:
    """Clear the session cookie."""
    response.delete_cookie(key=SESSION_COOKIE_NAME)


def get_current_user_optional(
    kumon_session: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME)
) -> Optional[User]:
    """Get the current user from session cookie (returns None if not logged in)."""
    if not kumon_session:
        return None
    return decode_session_token(kumon_session)


def get_current_user(
    kumon_session: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME)
) -> User:
    """Get the current user from session cookie (raises 401 if not logged in)."""
    if not kumon_session:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = decode_session_token(kumon_session)
    if not user:
        raise HTTPException(status_code=401, detail="Session expired")

    return user


def get_user_data_dir(user_id: str) -> Path:
    """Get the data directory for a specific user."""
    user_dir = Path(settings.data_dir) / "users" / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def get_user_token_path(user_id: str) -> Path:
    """Get the path to a user's Google token file."""
    return get_user_data_dir(user_id) / "google_token.json"
