"""
Audit log query endpoints.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models_db import User
from app.auth import get_current_user, require_role
from app.audit import get_audit_logs

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


@router.get("/logs")
def list_audit_logs(
    user_id: str = Query(None),
    action: str = Query(None),
    resource_type: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    return get_audit_logs(db, user_id, action, resource_type, limit, offset)


@router.get("/logs/me")
def my_audit_logs(
    action: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_audit_logs(db, current_user.id, action, limit=limit, offset=offset)
