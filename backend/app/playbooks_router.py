"""
Playbooks CRUD and execution endpoints.
"""
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.models_db import User, Playbook, PlaybookExecution
from app.auth import get_current_user, require_role
from app.audit import log_audit
from app.playbooks.engine import start_playbook, complete_step, get_execution_status

router = APIRouter(prefix="/api/v1/playbooks", tags=["playbooks"])


class PlaybookRequest(BaseModel):
    name: str
    description: Optional[str] = None
    alert_type: Optional[str] = None
    severity_threshold: Optional[str] = None
    steps: list
    is_enabled: bool = True

    model_config = {"json_schema_extra": {"examples": [{"name": "Ransomware Response", "description": "Standard ransomware incident response", "alert_type": "ransomware", "severity_threshold": "critical", "steps": [{"type": "manual", "label": "Isolate affected systems"}, {"type": "approval", "label": "Manager approval for containment"}, {"type": "auto", "label": "Collect forensic images"}]}]}}


class StepCompleteRequest(BaseModel):
    notes: Optional[str] = None


@router.get("")
def list_playbooks(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    playbooks = db.query(Playbook).filter(Playbook.user_id == user.id).all()
    return {
        "playbooks": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "alert_type": p.alert_type,
                "severity_threshold": p.severity_threshold,
                "steps": json.loads(p.steps),
                "is_enabled": p.is_enabled,
                "execution_count": p.execution_count,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in playbooks
        ]
    }


@router.post("")
def create_playbook(
    body: PlaybookRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "analyst")),
):
    playbook = Playbook(
        user_id=user.id,
        name=body.name,
        description=body.description,
        alert_type=body.alert_type,
        severity_threshold=body.severity_threshold,
        steps=json.dumps(body.steps),
        is_enabled=body.is_enabled,
    )
    db.add(playbook)
    db.commit()
    db.refresh(playbook)
    log_audit(db, user.id, "playbook.created", "playbook", str(playbook.id))
    return {"id": playbook.id, "message": "Created"}


@router.put("/{playbook_id}")
def update_playbook(
    playbook_id: int,
    body: PlaybookRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "analyst")),
):
    playbook = db.query(Playbook).filter(Playbook.id == playbook_id, Playbook.user_id == user.id).first()
    if not playbook:
        raise HTTPException(status_code=404, detail="Playbook not found")

    playbook.name = body.name
    playbook.description = body.description
    playbook.alert_type = body.alert_type
    playbook.severity_threshold = body.severity_threshold
    playbook.steps = json.dumps(body.steps)
    playbook.is_enabled = body.is_enabled
    db.commit()
    log_audit(db, user.id, "playbook.updated", "playbook", str(playbook_id))
    return {"message": "Updated"}


@router.delete("/{playbook_id}")
def delete_playbook(
    playbook_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "analyst")),
):
    playbook = db.query(Playbook).filter(Playbook.id == playbook_id, Playbook.user_id == user.id).first()
    if not playbook:
        raise HTTPException(status_code=404, detail="Playbook not found")
    db.delete(playbook)
    db.commit()
    log_audit(db, user.id, "playbook.deleted", "playbook", str(playbook_id))
    return {"message": "Deleted"}


@router.post("/{playbook_id}/execute")
def execute_playbook(
    playbook_id: int,
    alert_id: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "analyst")),
):
    try:
        execution = start_playbook(db, playbook_id, user.id, alert_id)
        log_audit(db, user.id, "playbook.executed", "playbook", str(playbook_id), {"execution_id": execution.id})
        return {"execution_id": execution.id, "message": "Started"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/executions/{execution_id}")
def get_execution(
    execution_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return get_execution_status(db, execution_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/executions/{execution_id}/steps/{step_index}")
def complete_playbook_step(
    execution_id: int,
    step_index: int,
    body: StepCompleteRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "analyst")),
):
    try:
        execution = complete_step(db, execution_id, step_index, body.notes)
        return {"status": execution.status, "message": "Step completed"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
