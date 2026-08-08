"""
Authentication endpoints: register, login, refresh, me, profile, user management.
"""
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.models_db import User, AuditLog
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
    require_role,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from jose import JWTError, jwt
import os

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "flare-dev-secret-change-in-production")
ALGORITHM = "HS256"

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: str
    name: str
    password: str

    model_config = {"json_schema_extra": {"examples": [{"email": "analyst@flare.dev", "name": "Jane Doe", "password": "securepass123"}]}}


class LoginRequest(BaseModel):
    email: str
    password: str

    model_config = {"json_schema_extra": {"examples": [{"email": "analyst@flare.dev", "password": "securepass123"}]}}


class RefreshRequest(BaseModel):
    refresh_token: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class UserUpdateRequest(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None
    name: Optional[str] = None


def _log_audit(db: Session, user_id: str, action: str, ip: Optional[str] = None, details: Optional[str] = None):
    db.add(AuditLog(
        user_id=user_id,
        action=action,
        resource_type="user",
        resource_id=user_id,
        details=details,
        ip_address=ip,
    ))
    db.commit()


def _user_dict(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@router.post("/register", response_model=AuthResponse)
def register(body: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    user = User(
        email=body.email,
        name=body.name,
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access = create_access_token({"sub": user.id})
    refresh = create_refresh_token({"sub": user.id})
    _log_audit(db, user.id, "user.register", request.client.host if request.client else None)

    return AuthResponse(
        access_token=access,
        refresh_token=refresh,
        user=_user_dict(user),
    )


@router.post("/login", response_model=AuthResponse)
def login(body: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    access = create_access_token({"sub": user.id})
    refresh = create_refresh_token({"sub": user.id})
    _log_audit(db, user.id, "user.login", request.client.host if request.client else None)

    return AuthResponse(
        access_token=access,
        refresh_token=refresh,
        user=_user_dict(user),
    )


@router.post("/refresh")
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(body.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        token_type = payload.get("type")
        if user_id is None or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    access = create_access_token({"sub": user.id})
    refresh_new = create_refresh_token({"sub": user.id})
    return {"access_token": access, "refresh_token": refresh_new, "token_type": "bearer"}


@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return _user_dict(user)


@router.put("/profile")
def update_profile(
    body: ProfileUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if body.email and body.email != user.email:
        if db.query(User).filter(User.email == body.email, User.id != user.id).first():
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = body.email
    if body.name:
        user.name = body.name
    db.commit()
    _log_audit(db, user.id, "user.profile_updated", request.client.host if request.client else None)
    return _user_dict(user)


@router.post("/change-password")
def change_password(
    body: ChangePasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not verify_password(body.current_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    user.hashed_password = hash_password(body.new_password)
    db.commit()
    _log_audit(db, user.id, "user.password_changed", request.client.host if request.client else None)
    return {"message": "Password updated"}


@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return {"users": [_user_dict(u) for u in users]}


@router.put("/users/{user_id}")
def update_user(
    user_id: str,
    body: UserUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if body.role is not None:
        if body.role not in ("admin", "analyst", "viewer"):
            raise HTTPException(status_code=400, detail="Invalid role")
        target.role = body.role
    if body.is_active is not None:
        target.is_active = body.is_active
    if body.name:
        target.name = body.name
    db.commit()
    _log_audit(
        db, user.id, "user.admin_updated", request.client.host if request.client else None,
        json.dumps({"target_user_id": user_id, "changes": body.model_dump(exclude_none=True)}),
    )
    return _user_dict(target)


@router.delete("/users/{user_id}")
def deactivate_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    if user_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    target.is_active = False
    db.commit()
    _log_audit(
        db, user.id, "user.admin_deactivated", request.client.host if request.client else None,
        json.dumps({"target_user_id": user_id}),
    )
    return {"message": "User deactivated"}
