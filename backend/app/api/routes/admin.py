from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session

from app.core.security import AuthContext, audit, require_admin, require_csrf
from app.db.session import get_db
from app.models import AuthSession, BirthProfile, User
from app.models.entities import utcnow
from app.schemas.admin import AdminSummary, AdminUserRead

router = APIRouter(prefix="/admin", tags=["administration"])
STATUS_FILTERS = {
    "pending": (User.is_active.is_(True), User.role != "admin", User.approved_at.is_(None)),
    "approved": (User.is_active.is_(True), or_(User.role == "admin", User.approved_at.is_not(None))),
    "inactive": (User.is_active.is_(False),),
    "all": (),
}


def admin_action(context: AuthContext = Depends(require_csrf)) -> AuthContext:
    if context.user.role != "admin": raise HTTPException(403, "Administrator access required")
    return context


def account_status(user: User) -> str:
    if not user.is_active: return "inactive"
    return "approved" if user.role == "admin" or user.approved_at else "pending"


def admin_user_read(user: User, profile_count: int) -> dict:
    return {"id": user.id, "full_name": user.full_name, "email": user.email or "", "role": user.role, "status": account_status(user),
        "email_verified": user.email_verified_at is not None, "approved_at": user.approved_at, "created_at": user.created_at,
        "last_login_at": user.last_login_at, "deletion_requested_at": user.deletion_requested_at, "profile_count": profile_count}


def target_user(db: Session, user_id: int) -> User:
    if not (user := db.get(User, user_id)): raise HTTPException(404, "User not found")
    return user


@router.get("/summary", response_model=AdminSummary)
def summary(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return {status: db.scalar(select(func.count(User.id)).where(*conditions)) or 0 for status, conditions in STATUS_FILTERS.items()}


@router.get("/users", response_model=list[AdminUserRead])
def list_users(status: Literal["pending", "approved", "inactive", "all"] = "pending", admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    counts = dict(db.execute(select(BirthProfile.user_id, func.count(BirthProfile.id)).group_by(BirthProfile.user_id)).all())
    users = db.scalars(select(User).where(*STATUS_FILTERS[status]).order_by(User.created_at.desc(), User.id.desc()))
    return [admin_user_read(user, counts.get(user.id, 0)) for user in users]


@router.post("/users/{user_id}/approve", response_model=AdminUserRead)
def approve(user_id: int, request: Request, context: AuthContext = Depends(admin_action), db: Session = Depends(get_db)):
    user = target_user(db, user_id)
    if not user.is_active: raise HTTPException(409, "Reactivate the account before approving it")
    if user.role != "admin" and user.approved_at is None:
        user.approved_at, user.approved_by_id = utcnow(), context.user.id
        audit(db, request, "admin.user_approve", "success", context.user.id, f"user {user.id}")
        db.commit()
    return admin_user_read(user, db.scalar(select(func.count(BirthProfile.id)).where(BirthProfile.user_id == user.id)) or 0)


@router.post("/users/{user_id}/deactivate", response_model=AdminUserRead)
def deactivate(user_id: int, request: Request, context: AuthContext = Depends(admin_action), db: Session = Depends(get_db)):
    user = target_user(db, user_id)
    if user.id == context.user.id: raise HTTPException(400, "You cannot deactivate your own account")
    if user.role == "admin": raise HTTPException(409, "Administrator accounts cannot be deactivated from the dashboard")
    if user.is_active:
        user.is_active = False
        db.execute(update(AuthSession).where(AuthSession.user_id == user.id, AuthSession.revoked_at.is_(None)).values(revoked_at=utcnow()))
        audit(db, request, "admin.user_deactivate", "success", context.user.id, f"user {user.id}")
        db.commit()
    return admin_user_read(user, db.scalar(select(func.count(BirthProfile.id)).where(BirthProfile.user_id == user.id)) or 0)


@router.post("/users/{user_id}/reactivate", response_model=AdminUserRead)
def reactivate(user_id: int, request: Request, context: AuthContext = Depends(admin_action), db: Session = Depends(get_db)):
    user = target_user(db, user_id)
    if not user.is_active:
        user.is_active = True
        audit(db, request, "admin.user_reactivate", "success", context.user.id, f"user {user.id}")
        db.commit()
    return admin_user_read(user, db.scalar(select(func.count(BirthProfile.id)).where(BirthProfile.user_id == user.id)) or 0)
