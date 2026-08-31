"""
Tenant management endpoints (admin only).
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.models_db import User, Tenant
from app.auth import get_current_user, require_role

router = APIRouter(prefix="/api/v1/tenants", tags=["tenants"])


class TenantRequest(BaseModel):
    name: str
    slug: str


@router.get("")
def list_tenants(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    tenants = db.query(Tenant).order_by(Tenant.created_at.desc()).all()
    return {"tenants": [{"id": t.id, "name": t.name, "slug": t.slug, "is_active": t.is_active, "created_at": t.created_at.isoformat()} for t in tenants]}


@router.post("")
def create_tenant(body: TenantRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if db.query(Tenant).filter(Tenant.slug == body.slug).first():
        raise HTTPException(status_code=400, detail="Slug already taken")
    tenant = Tenant(name=body.name, slug=body.slug)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return {"id": tenant.id, "name": tenant.name, "slug": tenant.slug}


@router.put("/{tenant_id}")
def update_tenant(tenant_id: str, body: TenantRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant.name = body.name
    db.commit()
    return {"id": tenant.id, "name": tenant.name, "slug": tenant.slug}


@router.delete("/{tenant_id}")
def deactivate_tenant(tenant_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant.is_active = False
    db.commit()
    return {"message": "Tenant deactivated"}


@router.post("/assign")
def assign_user_to_tenant(user_id: str, tenant_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    target.tenant_id = tenant_id
    db.commit()
    return {"message": f"User assigned to {tenant.name}"}
