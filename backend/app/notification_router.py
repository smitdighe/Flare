"""
Notification preference endpoints.
"""
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.models_db import User, NotificationPreference
from app.auth import get_current_user

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


class NotificationPrefRequest(BaseModel):
    channel: str
    event_type: str
    is_enabled: bool = True
    config: Optional[dict] = None


@router.get("/preferences")
def list_preferences(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    prefs = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user.id
    ).all()
    return {
        "preferences": [
            {
                "id": p.id,
                "channel": p.channel,
                "event_type": p.event_type,
                "is_enabled": p.is_enabled,
                "config": json.loads(p.config) if p.config else None,
            }
            for p in prefs
        ]
    }


@router.post("/preferences")
def create_preference(
    body: NotificationPrefRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    existing = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user.id,
        NotificationPreference.channel == body.channel,
        NotificationPreference.event_type == body.event_type,
    ).first()
    if existing:
        existing.is_enabled = body.is_enabled
        existing.config = json.dumps(body.config) if body.config else None
        db.commit()
        return {"id": existing.id, "message": "Updated"}

    pref = NotificationPreference(
        user_id=user.id,
        channel=body.channel,
        event_type=body.event_type,
        is_enabled=body.is_enabled,
        config=json.dumps(body.config) if body.config else None,
    )
    db.add(pref)
    db.commit()
    return {"id": pref.id, "message": "Created"}


@router.delete("/preferences/{pref_id}")
def delete_preference(
    pref_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    pref = db.query(NotificationPreference).filter(
        NotificationPreference.id == pref_id,
        NotificationPreference.user_id == user.id,
    ).first()
    if not pref:
        raise HTTPException(status_code=404, detail="Preference not found")
    db.delete(pref)
    db.commit()
    return {"message": "Deleted"}
