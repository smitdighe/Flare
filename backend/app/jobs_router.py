"""
Background jobs management endpoints (admin only).
"""
from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_role
from app.models_db import User
from app.scheduler import get_jobs, trigger_job

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.get("")
def list_jobs(user: User = Depends(require_role("admin"))):
    return {"jobs": get_jobs()}


@router.post("/{job_id}/trigger")
def run_job(job_id: str, user: User = Depends(require_role("admin"))):
    try:
        return trigger_job(job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
