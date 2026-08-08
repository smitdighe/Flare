"""
Playbook execution engine.
"""
import json
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models_db import Playbook, PlaybookExecution


def start_playbook(
    db: Session,
    playbook_id: int,
    user_id: str,
    alert_id: Optional[str] = None,
) -> PlaybookExecution:
    playbook = db.query(Playbook).filter(Playbook.id == playbook_id).first()
    if not playbook:
        raise ValueError("Playbook not found")

    execution = PlaybookExecution(
        playbook_id=playbook_id,
        alert_id=alert_id,
        user_id=user_id,
        status="in_progress",
        current_step=0,
        completed_steps="[]",
    )
    db.add(execution)
    playbook.execution_count += 1
    db.commit()
    db.refresh(execution)
    return execution


def complete_step(db: Session, execution_id: int, step_index: int, notes: Optional[str] = None):
    execution = db.query(PlaybookExecution).filter(PlaybookExecution.id == execution_id).first()
    if not execution:
        raise ValueError("Execution not found")

    completed = json.loads(execution.completed_steps)
    if step_index not in completed:
        completed.append(step_index)
    execution.completed_steps = json.dumps(completed)
    execution.current_step = step_index + 1

    if notes:
        execution.notes = (execution.notes or "") + f"\nStep {step_index}: {notes}"

    playbook = db.query(Playbook).filter(Playbook.id == execution.playbook_id).first()
    steps = json.loads(playbook.steps) if playbook else []
    if execution.current_step >= len(steps):
        execution.status = "completed"
        execution.completed_at = datetime.now(timezone.utc)

    db.commit()
    return execution


def get_execution_status(db: Session, execution_id: int) -> dict:
    execution = db.query(PlaybookExecution).filter(PlaybookExecution.id == execution_id).first()
    if not execution:
        raise ValueError("Execution not found")

    playbook = db.query(Playbook).filter(Playbook.id == execution.playbook_id).first()
    steps = json.loads(playbook.steps) if playbook else []
    completed = json.loads(execution.completed_steps)

    return {
        "id": execution.id,
        "playbook_id": execution.playbook_id,
        "alert_id": execution.alert_id,
        "status": execution.status,
        "current_step": execution.current_step,
        "total_steps": len(steps),
        "completed_steps": completed,
        "steps": steps,
        "notes": execution.notes,
        "started_at": execution.started_at.isoformat() if execution.started_at else None,
        "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
    }
