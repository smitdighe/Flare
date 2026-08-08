"""
Rules CRUD endpoints.
"""
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.models_db import User, Rule
from app.auth import get_current_user, require_role
from app.audit import log_audit

router = APIRouter(prefix="/api/v1/rules", tags=["rules"])


class RuleRequest(BaseModel):
    name: str
    description: Optional[str] = None
    is_enabled: bool = True
    priority: int = 0
    conditions: dict
    actions: list

    model_config = {"json_schema_extra": {"examples": [{"name": "High Severity Alert", "description": "Auto-escalate critical alerts", "conditions": {"field": "severity", "op": "equals", "value": "high"}, "actions": [{"type": "notify", "channel": "slack"}]}]}}


@router.get("")
def list_rules(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rules = db.query(Rule).filter(Rule.user_id == user.id).order_by(Rule.priority.desc()).all()
    return {
        "rules": [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "is_enabled": r.is_enabled,
                "priority": r.priority,
                "conditions": json.loads(r.conditions),
                "actions": json.loads(r.actions),
                "match_count": r.match_count,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rules
        ]
    }


@router.post("")
def create_rule(
    body: RuleRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "analyst")),
):
    rule = Rule(
        user_id=user.id,
        name=body.name,
        description=body.description,
        is_enabled=body.is_enabled,
        priority=body.priority,
        conditions=json.dumps(body.conditions),
        actions=json.dumps(body.actions),
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    log_audit(db, user.id, "rule.created", "rule", str(rule.id))
    return {"id": rule.id, "message": "Created"}


@router.put("/{rule_id}")
def update_rule(
    rule_id: int,
    body: RuleRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "analyst")),
):
    rule = db.query(Rule).filter(Rule.id == rule_id, Rule.user_id == user.id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    rule.name = body.name
    rule.description = body.description
    rule.is_enabled = body.is_enabled
    rule.priority = body.priority
    rule.conditions = json.dumps(body.conditions)
    rule.actions = json.dumps(body.actions)
    db.commit()
    log_audit(db, user.id, "rule.updated", "rule", str(rule_id))
    return {"message": "Updated"}


@router.delete("/{rule_id}")
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "analyst")),
):
    rule = db.query(Rule).filter(Rule.id == rule_id, Rule.user_id == user.id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    log_audit(db, user.id, "rule.deleted", "rule", str(rule_id))
    return {"message": "Deleted"}
