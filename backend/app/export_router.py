"""
Export endpoints: CSV and PDF download.
"""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models_db import User
from app.auth import get_current_user
from app.store import store
from app.export.csv_export import generate_csv
from app.export.pdf_export import generate_pdf

router = APIRouter(prefix="/api/v1/export", tags=["export"])


@router.get("/alerts/csv")
def export_csv(
    severity: str = Query(None),
    attack_type: str = Query(None),
    search: str = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    user: User = Depends(get_current_user),
):
    result = store.filter(severity=severity, attack_type=attack_type, search=search, limit=limit)
    csv_content = generate_csv(result["alerts"])
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=flare_alerts.csv"},
    )


@router.get("/alerts/pdf")
def export_pdf(
    severity: str = Query(None),
    attack_type: str = Query(None),
    search: str = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    user: User = Depends(get_current_user),
):
    result = store.filter(severity=severity, attack_type=attack_type, search=search, limit=limit)
    stats = store.stats()
    pdf_content = generate_pdf(result["alerts"], stats=stats)
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=flare_report.pdf"},
    )
