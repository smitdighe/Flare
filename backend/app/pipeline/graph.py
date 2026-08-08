"""
Flare's LangGraph pipeline: classify -> enrich -> reason -> END

Enrich and reason both skip low-severity alerts (they short-circuit
internally and return empty fields fast) - this matches the project spec:
only medium/high severity alerts get the expensive enrichment + reasoning
treatment, keeping API usage sane on free tiers.
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

from app.pipeline.classify import classify_alert
from app.pipeline.enrich import enrich_alert
from app.pipeline.reason import reason_about_alert


class PipelineState(TypedDict):
    alert: dict
    severity: Optional[str]
    attack_type: Optional[str]
    classify_latency_ms: Optional[float]
    ioc_reputation: Optional[str]
    ioc_checked: Optional[bool]
    vt_ip: Optional[str]
    vt_hash: Optional[str]
    enrich_latency_ms: Optional[float]
    explanation: Optional[str]
    mitre_technique: Optional[str]
    remediation: Optional[list]
    reasoning_latency_ms: Optional[float]


def classify_node(state: PipelineState) -> PipelineState:
    result = classify_alert(state["alert"])
    return {**state, **result}


def enrich_node(state: PipelineState) -> PipelineState:
    merged_alert = {**state["alert"], **state}
    result = enrich_alert(merged_alert)
    return {**state, **result}


def reason_node(state: PipelineState) -> PipelineState:
    merged_alert = {**state["alert"], **state}
    result = reason_about_alert(merged_alert)
    return {**state, **result}


def build_pipeline():
    graph = StateGraph(PipelineState)
    graph.add_node("classify", classify_node)
    graph.add_node("enrich", enrich_node)
    graph.add_node("reason", reason_node)

    graph.set_entry_point("classify")
    graph.add_edge("classify", "enrich")
    graph.add_edge("enrich", "reason")
    graph.add_edge("reason", END)

    return graph.compile()


_pipeline = None


def get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = build_pipeline()
    return _pipeline


def run_pipeline(raw_alert: dict) -> dict:
    pipeline = get_pipeline()
    result = pipeline.invoke({"alert": raw_alert})
    return {**raw_alert, **{k: v for k, v in result.items() if k != "alert"}}
