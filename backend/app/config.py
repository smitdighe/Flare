"""
Pipeline configuration. Controls speed, stage toggles, and batch settings.
"""
from pydantic import BaseModel, Field
from typing import Literal


SPEED_INTERVALS = {
    "fast": 1.5,
    "balanced": 2.5,
    "thorough": 4.0,
}


class PipelineConfig(BaseModel):
    speed: Literal["fast", "balanced", "thorough"] = "balanced"
    classify_enabled: bool = True
    enrich_enabled: bool = True
    reason_enabled: bool = True
    batch_size: int = Field(default=1, ge=1, le=10)
    max_alerts: int = Field(default=500, ge=10, le=2000)

    @property
    def interval(self) -> float:
        return SPEED_INTERVALS[self.speed]


config = PipelineConfig()
