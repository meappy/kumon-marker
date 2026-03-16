"""API endpoints for dashboard sharing."""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr

from app.core.session import User, get_current_user
from app.models.job import Share, SharePermission, get_db, init_db

router = APIRouter()


class ShareRequest(BaseModel):
    """Request to share dashboard with another user."""

    email: EmailStr
    permission: str = SharePermission.READ.value


class ShareResponse(BaseModel):
    """A share entry."""

    id: str
    shared_with_email: str
    permission: str
    created_at: str


class SharedWithMeEntry(BaseModel):
    """A dashboard shared with the current user."""

    owner_user_id: str
    owner_email: str
    owner_name: str | None
    permission: str


@router.get("/shares")
async def list_shares(user: User = Depends(get_current_user)) -> list[ShareResponse]:
    """List emails the current user shares their dashboard with."""
    init_db()
    db = get_db()
    try:
        shares = db.query(Share).filter(Share.owner_user_id == user.id).all()
        return [
            ShareResponse(
                id=s.id,
                shared_with_email=s.shared_with_email,
                permission=s.permission,
                created_at=s.created_at.isoformat() if s.created_at else "",
            )
            for s in shares
        ]
    finally:
        db.close()


@router.post("/shares")
async def add_share(
    request: ShareRequest, user: User = Depends(get_current_user)
) -> ShareResponse:
    """Share dashboard with another user by email."""
    if request.email.lower() == user.email.lower():
        raise HTTPException(status_code=400, detail="Cannot share with yourself")

    if request.permission not in (
        SharePermission.READ.value,
        SharePermission.READWRITE.value,
    ):
        raise HTTPException(
            status_code=400, detail="Permission must be 'read' or 'readwrite'"
        )

    init_db()
    db = get_db()
    try:
        # Check if share already exists
        existing = (
            db.query(Share)
            .filter(
                Share.owner_user_id == user.id,
                Share.shared_with_email == request.email.lower(),
            )
            .first()
        )

        if existing:
            # Update permission if changed
            if existing.permission != request.permission:
                existing.permission = request.permission
                existing.updated_at = datetime.now(timezone.utc)
                db.commit()
                db.refresh(existing)
            return ShareResponse(
                id=existing.id,
                shared_with_email=existing.shared_with_email,
                permission=existing.permission,
                created_at=existing.created_at.isoformat()
                if existing.created_at
                else "",
            )

        share = Share(
            owner_user_id=user.id,
            owner_email=user.email,
            owner_name=user.name,
            shared_with_email=request.email.lower(),
            permission=request.permission,
        )
        db.add(share)
        db.commit()
        db.refresh(share)

        return ShareResponse(
            id=share.id,
            shared_with_email=share.shared_with_email,
            permission=share.permission,
            created_at=share.created_at.isoformat() if share.created_at else "",
        )
    finally:
        db.close()


@router.delete("/shares/{email}")
async def remove_share(email: str, user: User = Depends(get_current_user)):
    """Remove a shared email."""
    init_db()
    db = get_db()
    try:
        share = (
            db.query(Share)
            .filter(
                Share.owner_user_id == user.id,
                Share.shared_with_email == email.lower(),
            )
            .first()
        )
        if not share:
            raise HTTPException(status_code=404, detail="Share not found")

        db.delete(share)
        db.commit()
        return {"message": "Share removed"}
    finally:
        db.close()


@router.get("/shared-with-me")
async def shared_with_me(
    user: User = Depends(get_current_user),
) -> list[SharedWithMeEntry]:
    """List dashboards shared with the current user."""
    init_db()
    db = get_db()
    try:
        shares = (
            db.query(Share).filter(Share.shared_with_email == user.email.lower()).all()
        )
        return [
            SharedWithMeEntry(
                owner_user_id=s.owner_user_id,
                owner_email=s.owner_email,
                owner_name=s.owner_name,
                permission=s.permission,
            )
            for s in shares
        ]
    finally:
        db.close()
