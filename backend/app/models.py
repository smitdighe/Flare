from pydantic import BaseModel, Field
from typing import Literal, Optional


class RawAlert(BaseModel):
    id: str
    timestamp: str
    src_ip: str
    dest_ip: str
    dest_port: int
    protocol: str
    signature: str


class TriagedAlert(RawAlert):
    severity: Optional[str] = None
    attack_type: Optional[str] = None
    classify_latency_ms: Optional[float] = None

    ioc_reputation: Optional[str] = None
    ioc_checked: bool = False
    vt_ip: Optional[str] = None
    vt_hash: Optional[str] = None

    mitre_technique: Optional[str] = None
    explanation: Optional[str] = None
    remediation: Optional[list[str]] = None
    reasoning_latency_ms: Optional[float] = None


class AlertFilterParams(BaseModel):
    severity: Optional[str] = None
    attack_type: Optional[str] = None
    search: Optional[str] = None
    min_severity: Optional[str] = None
    limit: int = 50
    offset: int = 0


class StreamConfig(BaseModel):
    speed: Optional[Literal["fast", "balanced", "thorough"]] = None
    classify_enabled: Optional[bool] = None
    enrich_enabled: Optional[bool] = None
    reason_enabled: Optional[bool] = None
    batch_size: Optional[int] = Field(default=None, ge=1, le=10)
