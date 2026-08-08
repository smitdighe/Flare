"""
Controllable SSE stream manager. Supports pause/resume, speed control,
and batch size configuration.
"""
import asyncio
import json
import time
from dataclasses import dataclass, field

from app.config import config
from app.data.generator import generate_alert
from app.pipeline.graph import run_pipeline
from app.store import store


@dataclass
class StreamState:
    running: bool = True
    paused: bool = False
    alerts_sent: int = 0
    started_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        elapsed = time.time() - self.started_at
        return {
            "running": self.running,
            "paused": self.paused,
            "alerts_sent": self.alerts_sent,
            "uptime_seconds": round(elapsed, 1),
            "alerts_per_minute": round(self.alerts_sent / max(elapsed / 60, 0.01), 2),
        }


state = StreamState()


async def event_generator():
    pause_event = asyncio.Event()
    pause_event.set()

    while state.running:
        if state.paused:
            await pause_event.wait()

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
            state.alerts_sent += 1

        for alert in batch:
            yield f"data: {json.dumps(alert)}\n\n"

        await asyncio.sleep(config.interval)


_pause_event: asyncio.Event | None = None


def _get_pause_event() -> asyncio.Event:
    global _pause_event
    if _pause_event is None:
        _pause_event = asyncio.Event()
        _pause_event.set()
    return _pause_event


def pause_stream():
    state.paused = True
    ev = _get_pause_event()
    ev.clear()


def resume_stream():
    state.paused = False
    ev = _get_pause_event()
    ev.set()


def get_stream_state() -> dict:
    return state.to_dict()
