import asyncio
import json
import logging
import os
import threading
import time
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
logger = logging.getLogger("flare")

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Query, Request, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.responses import JSONResponse
from typing import Optional

from app.data.generator import generate_alert
from app.pipeline.graph import run_pipeline
from app.eval import run_eval
from app.pipeline.benchmark import run_benchmark
from app.store import store
from app.health import check_all
from app.config import config, SPEED_INTERVALS
from app.models import StreamConfig
from app import stream as stream_mod
from app.database import init_db, SessionLocal
from app.models_db import User, Alert, AuditLog
from app.auth import hash_password, get_current_user, require_role, SECRET_KEY, ALGORITHM
from app.auth_router import router as auth_router
from app.security import RateLimitMiddleware, sanitize_alert_data
from app.error_handlers import RequestIDMiddleware, global_exception_handler
from app.audit_router import router as audit_router
from app.notification_router import router as notification_router
from app.export_router import router as export_router
from app.rules_router import router as rules_router
from app.playbooks_router import router as playbooks_router
from app.jobs_router import router as jobs_router
from app.tenants_router import router as tenants_router
from app.database import SessionLocal
from app.scheduler import start_scheduler, stop_scheduler
from jose import JWTError, jwt

ALLOWED_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")

app = FastAPI(
    title="Flare Alert Triage API",
    description="Multi-agent security alert triage engine with AI-powered classification, enrichment, and reasoning.",
    version="2.0.0",
    contact={"name": "Flare Team", "email": "support@flare.dev"},
    license_info={"name": "MIT"},
    openapi_tags=[
        {"name": "auth", "description": "Authentication, registration, and user management"},
        {"name": "alerts", "description": "Alert listing, filtering, and detail views"},
        {"name": "stream", "description": "Real-time alert streaming (SSE and WebSocket)"},
        {"name": "rules", "description": "Custom alert rule creation and management"},
        {"name": "playbooks", "description": "Incident response playbook CRUD and execution"},
        {"name": "notifications", "description": "Email and Slack notification preferences"},
        {"name": "export", "description": "CSV and PDF alert export"},
        {"name": "audit", "description": "Audit log viewing"},
        {"name": "jobs", "description": "Background job scheduling and management"},
        {"name": "tenants", "description": "Multi-tenant organization management"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
app.add_middleware(RequestIDMiddleware)
app.add_exception_handler(500, global_exception_handler)
app.include_router(auth_router)
app.include_router(audit_router)
app.include_router(notification_router)
app.include_router(export_router)
app.include_router(rules_router)
app.include_router(playbooks_router)
app.include_router(jobs_router)
app.include_router(tenants_router)


@app.on_event("startup")
def startup():
    init_db()
    db = SessionLocal()
    should_seed = False
    try:
        if db.query(User).count() == 0:
            admin = User(
                email="admin@flare.dev",
                name="Admin",
                hashed_password=hash_password("admin123"),
                role="admin",
            )
            db.add(admin)
            db.commit()
            should_seed = True
    finally:
        db.close()
    if should_seed:
        threading.Thread(target=_seed_daemon, daemon=True).start()
    start_scheduler()


def _seed_daemon():
    from app.pipeline.classify import SIGNATURE_RULES
    signatures = list(SIGNATURE_RULES.keys())
    for i in range(12):
        try:
            sig = signatures[i % len(signatures)]
            severity, attack_type = SIGNATURE_RULES[sig]
            store.append({
                "id": f"ALT-{i+1:04d}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "src_ip": f"185.220.101.{i+10}",
                "dest_ip": f"10.24.0.{i+1}",
                "dest_port": [80, 443, 22, 3389, 8080][i % 5],
                "protocol": "TCP",
                "signature": sig,
                "severity": severity,
                "attack_type": attack_type,
                "ioc_reputation": 50,
                "ioc_checked": True,
                "vt_ip": "suspicious",
                "explanation": f"Classified as {severity} {attack_type} by rule lookup.",
                "mitre_technique": "T1190",
                "remediation": "Review and contain.",
                "classify_latency_ms": 0.0,
            })
        except Exception:
            pass


@app.on_event("shutdown")
def shutdown():
    stop_scheduler()


def _wrap(data, meta=None):
    return {"ok": True, "data": data, "meta": meta or {}}


# ── Legacy endpoints (backward compat) ──

@app.get("/health")
def health():
    return {"status": "ok", "alerts_stored": store.count()}


@app.get("/api/health")
def api_health():
    return check_all()


@app.get("/api/v1/health")
def v1_health(user: User = Depends(get_current_user)):
    return check_all()


@app.get("/alerts/stream")
async def stream_alerts(user: User = Depends(get_current_user)):
    async def event_generator():
        while True:
            raw = generate_alert()
            triaged = run_pipeline(raw)
            store.append(triaged)
            yield f"data: {json.dumps(triaged)}\n\n"
            await asyncio.sleep(2.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/alerts")
def get_alerts(
    severity: Optional[str] = Query(None),
    attack_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    min_severity: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
):
    return store.filter(
        severity=severity,
        attack_type=attack_type,
        search=search,
        min_severity=min_severity,
        limit=limit,
        offset=offset,
    )


@app.get("/alerts/correlated")
def get_correlated(min_alerts: int = Query(2, ge=2, le=50), user: User = Depends(get_current_user)):
    return {"clusters": store.correlate(min_alerts=min_alerts)}


@app.get("/stats")
def get_stats(user: User = Depends(get_current_user)):
    return store.stats()


@app.get("/eval")
def get_eval(force: bool = Query(False), user: User = Depends(get_current_user)):
    return run_eval(force=force)


@app.get("/benchmark")
def get_benchmark(user: User = Depends(get_current_user)):
    alert = generate_alert()
    return run_benchmark(alert)


@app.post("/alerts/seed")
def seed_alerts(count: int = Query(10, ge=1, le=100), user: User = Depends(get_current_user)):
    for _ in range(count):
        raw = generate_alert()
        triaged = run_pipeline(raw)
        store.append(triaged)
    return {"seeded": count, "total": store.count()}


# ── Versioned API v1 ──

@app.get("/api/v1/alerts")
def v1_alerts(
    severity: Optional[str] = Query(None),
    attack_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    min_severity: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
):
    t0 = time.time()
    result = store.filter(
        severity=severity,
        attack_type=attack_type,
        search=search,
        min_severity=min_severity,
        limit=limit,
        offset=offset,
    )
    latency = round((time.time() - t0) * 1000, 2)
    return _wrap(result, {"count": result["total"], "latency_ms": latency})


@app.get("/api/v1/alerts/{alert_id}")
def v1_alert_detail(alert_id: str, user: User = Depends(get_current_user)):
    t0 = time.time()
    alert = store.get_by_id(alert_id)
    latency = round((time.time() - t0) * 1000, 2)
    if not alert:
        return JSONResponse(
            status_code=404,
            content={"ok": False, "error": "Alert not found", "meta": {"latency_ms": latency}},
        )

    pipeline_trace = {
        "classify": {
            "completed": alert.get("classify_latency_ms") is not None,
            "latency_ms": alert.get("classify_latency_ms"),
            "result": {
                "severity": alert.get("severity"),
                "attack_type": alert.get("attack_type"),
            } if alert.get("severity") else None,
        },
        "enrich": {
            "completed": alert.get("ioc_checked", False),
            "latency_ms": alert.get("enrich_latency_ms"),
            "result": {
                "ioc_reputation": alert.get("ioc_reputation"),
                "vt_ip": alert.get("vt_ip"),
                "vt_hash": alert.get("vt_hash"),
            } if alert.get("ioc_checked") else None,
        },
        "reason": {
            "completed": alert.get("explanation") is not None,
            "latency_ms": alert.get("reasoning_latency_ms"),
            "result": {
                "mitre_technique": alert.get("mitre_technique"),
                "explanation": alert.get("explanation"),
                "remediation": alert.get("remediation"),
            } if alert.get("explanation") else None,
        },
    }

    total_latency = sum(
        v for v in [
            alert.get("classify_latency_ms"),
            alert.get("enrich_latency_ms"),
            alert.get("reasoning_latency_ms"),
        ] if v
    )

    return _wrap(
        {**alert, "pipeline_trace": pipeline_trace, "total_pipeline_ms": round(total_latency, 1)},
        {"latency_ms": latency},
    )


@app.get("/api/v1/alerts/correlated/list")
def v1_correlated(min_alerts: int = Query(2, ge=2, le=50), user: User = Depends(get_current_user)):
    t0 = time.time()
    clusters = store.correlate(min_alerts=min_alerts)
    latency = round((time.time() - t0) * 1000, 2)
    return _wrap({"clusters": clusters}, {"count": len(clusters), "latency_ms": latency})


@app.get("/api/v1/stats")
def v1_stats(user: User = Depends(get_current_user)):
    t0 = time.time()
    stats = store.stats()
    latency = round((time.time() - t0) * 1000, 2)
    return _wrap(stats, {"latency_ms": latency})


@app.get("/api/v1/stream")
async def v1_stream(
    token: Optional[str] = Query(None),
    credentials: Optional[str] = None,
    user: User = Depends(get_current_user),
):
    return StreamingResponse(stream_mod.event_generator(), media_type="text/event-stream")


@app.get("/api/v1/stream/token")
async def v1_stream_token(token: Optional[str] = Query(None)):
    """SSE stream that accepts JWT via query param (for EventSource)."""
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        token_type = payload.get("type")
        if user_id is None or token_type != "access":
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user or not db_user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")
    finally:
        db.close()
    return StreamingResponse(stream_mod.event_generator(), media_type="text/event-stream")


@app.get("/api/v1/stream/status")
def v1_stream_status(user: User = Depends(get_current_user)):
    return _wrap(stream_mod.get_stream_state())


@app.post("/api/v1/stream/pause")
def v1_stream_pause(user: User = Depends(get_current_user)):
    stream_mod.pause_stream()
    return _wrap({"paused": True})


@app.post("/api/v1/stream/resume")
def v1_stream_resume(user: User = Depends(get_current_user)):
    stream_mod.resume_stream()
    return _wrap({"paused": False})


@app.post("/api/v1/stream/config")
def v1_stream_config(body: StreamConfig, user: User = Depends(get_current_user)):
    if body.speed is not None:
        speed: str = body.speed
        config.speed = speed  # type: ignore[assignment]
    if body.classify_enabled is not None:
        config.classify_enabled = body.classify_enabled
    if body.enrich_enabled is not None:
        config.enrich_enabled = body.enrich_enabled
    if body.reason_enabled is not None:
        config.reason_enabled = body.reason_enabled
    if body.batch_size is not None:
        config.batch_size = body.batch_size
    return _wrap(config.model_dump(), {"message": "Pipeline config updated"})


@app.get("/api/v1/config")
def v1_config(user: User = Depends(get_current_user)):
    return _wrap(config.model_dump())


@app.get("/api/v1/eval")
def v1_eval(force: bool = Query(False), user: User = Depends(get_current_user)):
    t0 = time.time()
    result = run_eval(force=force)
    latency = round((time.time() - t0) * 1000, 2)
    return _wrap(result, {"latency_ms": latency, "cached": latency < 5})


@app.get("/api/v1/benchmark")
def v1_benchmark(user: User = Depends(get_current_user)):
    t0 = time.time()
    alert = generate_alert()
    result = run_benchmark(alert)
    latency = round((time.time() - t0) * 1000, 2)
    return _wrap(result, {"latency_ms": latency})


@app.post("/api/v1/seed")
def v1_seed(count: int = Query(10, ge=1, le=100), user: User = Depends(get_current_user)):
    t0 = time.time()
    for _ in range(count):
        raw = generate_alert()
        triaged = run_pipeline(raw)
        store.append(triaged)
    latency = round((time.time() - t0) * 1000, 2)
    return _wrap({"seeded": count, "total": store.count()}, {"latency_ms": latency})


@app.websocket("/api/v1/ws/stream")
async def ws_stream(websocket: WebSocket, token: Optional[str] = Query(None)):
    """WebSocket endpoint for real-time alert streaming with auth via query param."""
    if not token:
        await websocket.close(code=4001, reason="Token required")
        return
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        token_type = payload.get("type")
        if user_id is None or token_type != "access":
            await websocket.close(code=4001, reason="Invalid token")
            return
    except JWTError:
        await websocket.close(code=4001, reason="Invalid token")
        return
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user or not db_user.is_active:
            await websocket.close(code=4003, reason="User inactive")
            return
    finally:
        db.close()

    await websocket.accept()
    try:
        while True:
            # Check for incoming messages (pause/resume/config commands)
            try:
                msg = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                cmd = json.loads(msg)
                if cmd.get("type") == "pause":
                    stream_mod.pause_stream()
                elif cmd.get("type") == "resume":
                    stream_mod.resume_stream()
                elif cmd.get("type") == "config":
                    speed = cmd.get("speed")
                    if speed and speed in SPEED_INTERVALS:
                        config.speed = speed
            except asyncio.TimeoutError:
                pass
            except json.JSONDecodeError:
                pass

            if stream_mod.state.paused:
                await asyncio.sleep(0.5)
                continue

            batch = []
            for _ in range(config.batch_size):
                raw = generate_alert()
                triaged = run_pipeline(raw)
                if not config.enrich_enabled:
                    triaged["ioc_checked"] = False
                    triaged["ioc_reputation"] = None
                    triaged["vt_ip"] = None
                    triaged["vt_hash"] = None
                if not config.reason_enabled:
                    triaged["explanation"] = None
                    triaged["mitre_technique"] = None
                    triaged["remediation"] = None
                store.append(triaged)
                batch.append(triaged)
                stream_mod.state.alerts_sent += 1

            for alert in batch:
                await websocket.send_json(alert)

            await asyncio.sleep(config.interval)
    except WebSocketDisconnect:
        pass
    except Exception:
        try:
            await websocket.close(code=1011, reason="Internal error")
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
