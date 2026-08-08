import asyncio
import json
import os
import time

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Query
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

ALLOWED_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")

app = FastAPI(title="Flare Alert Triage API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _wrap(data, meta=None):
    return {"ok": True, "data": data, "meta": meta or {}}


# ── Legacy endpoints (backward compat) ──

@app.get("/health")
def health():
    return {"status": "ok", "alerts_stored": store.count()}


@app.get("/api/health")
def api_health():
    return check_all()


@app.get("/alerts/stream")
async def stream_alerts():
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
def get_correlated(min_alerts: int = Query(2, ge=2, le=50)):
    return {"clusters": store.correlate(min_alerts=min_alerts)}


@app.get("/stats")
def get_stats():
    return store.stats()


@app.get("/eval")
def get_eval():
    return run_eval()


@app.get("/benchmark")
def get_benchmark():
    alert = generate_alert()
    return run_benchmark(alert)


@app.post("/alerts/seed")
def seed_alerts(count: int = Query(10, ge=1, le=100)):
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
def v1_alert_detail(alert_id: str):
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
def v1_correlated(min_alerts: int = Query(2, ge=2, le=50)):
    t0 = time.time()
    clusters = store.correlate(min_alerts=min_alerts)
    latency = round((time.time() - t0) * 1000, 2)
    return _wrap({"clusters": clusters}, {"count": len(clusters), "latency_ms": latency})


@app.get("/api/v1/stats")
def v1_stats():
    t0 = time.time()
    stats = store.stats()
    latency = round((time.time() - t0) * 1000, 2)
    return _wrap(stats, {"latency_ms": latency})


@app.get("/api/v1/stream")
async def v1_stream():
    return StreamingResponse(stream_mod.event_generator(), media_type="text/event-stream")


@app.get("/api/v1/stream/status")
def v1_stream_status():
    return _wrap(stream_mod.get_stream_state())


@app.post("/api/v1/stream/pause")
def v1_stream_pause():
    stream_mod.pause_stream()
    return _wrap({"paused": True})


@app.post("/api/v1/stream/resume")
def v1_stream_resume():
    stream_mod.resume_stream()
    return _wrap({"paused": False})


@app.post("/api/v1/stream/config")
def v1_stream_config(body: StreamConfig):
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
def v1_config():
    return _wrap(config.model_dump())


@app.get("/api/v1/eval")
def v1_eval():
    t0 = time.time()
    result = run_eval()
    latency = round((time.time() - t0) * 1000, 2)
    return _wrap(result, {"latency_ms": latency})


@app.get("/api/v1/benchmark")
def v1_benchmark():
    t0 = time.time()
    alert = generate_alert()
    result = run_benchmark(alert)
    latency = round((time.time() - t0) * 1000, 2)
    return _wrap(result, {"latency_ms": latency})


@app.get("/api/v1/health")
def v1_health():
    t0 = time.time()
    result = check_all()
    latency = round((time.time() - t0) * 1000, 2)
    return _wrap(result, {"latency_ms": latency})


@app.post("/api/v1/seed")
def v1_seed(count: int = Query(10, ge=1, le=100)):
    t0 = time.time()
    for _ in range(count):
        raw = generate_alert()
        triaged = run_pipeline(raw)
        store.append(triaged)
    latency = round((time.time() - t0) * 1000, 2)
    return _wrap({"seeded": count, "total": store.count()}, {"latency_ms": latency})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
