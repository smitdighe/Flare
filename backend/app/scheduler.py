"""
Background task scheduler using APScheduler.
Provides periodic jobs for cleanup, metrics, and notifications.
"""
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def _cleanup_stale_alerts():
    """Remove alerts older than 90 days."""
    from app.database import SessionLocal
    from app.models_db import Alert
    db = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=90)
        deleted = db.query(Alert).filter(Alert.created_at < cutoff).delete()
        db.commit()
        if deleted:
            logger.info(f"Cleaned up {deleted} stale alerts")
    except Exception as e:
        logger.error(f"Stale alert cleanup failed: {e}")
        db.rollback()
    finally:
        db.close()


def _aggregate_metrics():
    """Aggregate alert metrics for faster queries."""
    from app.database import SessionLocal
    from app.models_db import Alert
    db = SessionLocal()
    try:
        total = db.query(Alert).count()
        by_severity = {}
        for sev in ["critical", "high", "medium", "low", "info"]:
            count = db.query(Alert).filter(Alert.severity == sev).count()
            if count:
                by_severity[sev] = count
        logger.debug(f"Metrics aggregation: {total} alerts, severity breakdown: {by_severity}")
    except Exception as e:
        logger.error(f"Metrics aggregation failed: {e}")
    finally:
        db.close()


def _cleanup_old_audit_logs():
    """Remove audit logs older than 180 days."""
    from app.database import SessionLocal
    from app.models_db import AuditLog
    db = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=180)
        deleted = db.query(AuditLog).filter(AuditLog.created_at < cutoff).delete()
        db.commit()
        if deleted:
            logger.info(f"Cleaned up {deleted} old audit logs")
    except Exception as e:
        logger.error(f"Audit log cleanup failed: {e}")
        db.rollback()
    finally:
        db.close()


JOBS = {
    "cleanup_stale_alerts": {
        "func": _cleanup_stale_alerts,
        "trigger": IntervalTrigger(hours=6),
        "description": "Remove alerts older than 90 days",
    },
    "aggregate_metrics": {
        "func": _aggregate_metrics,
        "trigger": IntervalTrigger(minutes=30),
        "description": "Aggregate alert metrics for dashboards",
    },
    "cleanup_audit_logs": {
        "func": _cleanup_old_audit_logs,
        "trigger": CronTrigger(hour=3, minute=0),  # 3 AM daily
        "description": "Remove audit logs older than 180 days",
    },
}


def start_scheduler():
    """Start the scheduler with all configured jobs."""
    if scheduler.running:
        return
    for job_id, job_config in JOBS.items():
        scheduler.add_job(
            job_config["func"],
            trigger=job_config["trigger"],
            id=job_id,
            replace_existing=True,
        )
    scheduler.start()
    logger.info(f"Scheduler started with {len(JOBS)} jobs")


def stop_scheduler():
    """Stop the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")


def get_jobs():
    """Get info about all scheduled jobs."""
    jobs = []
    for job_id, job_config in JOBS.items():
        job = scheduler.get_job(job_id)
        jobs.append({
            "id": job_id,
            "description": job_config["description"],
            "next_run": job.next_run_time.isoformat() if job and job.next_run_time else None,
            "active": job is not None,
        })
    return jobs


def trigger_job(job_id: str):
    """Manually trigger a job by ID."""
    if job_id not in JOBS:
        raise ValueError(f"Unknown job: {job_id}")
    JOBS[job_id]["func"]()
    return {"job_id": job_id, "triggered": True}
