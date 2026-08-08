"""
Powers the provider benchmark toggle: runs the SAME alert through both the
fast-tier model (Groq) and the quality-tier model (Gemini), side by side,
so the dashboard can show a real latency/quality trade-off instead of just
asserting one exists.
"""
import json
import os
import time

import google.generativeai as genai

from app.pipeline.classify import classify_alert, _get_client as _get_groq_client

QUALITY_PROMPT = """You are a careful, thorough security alert classifier.
Given a single IDS alert, analyze it and respond with ONLY a JSON object, no other text:
{{"severity": "low" | "medium" | "high", "attack_type": "port_scan" | "ddos" | "malware" | "sql_injection" | "brute_force" | "other", "confidence_note": "one short sentence on your reasoning"}}

Signature: {signature}
Source IP: {src_ip} -> Dest: {dest_ip}:{dest_port} ({protocol})
"""

_configured = False


def _classify_quality_tier(alert: dict) -> dict:
    """Same task as the fast classifier, but via Gemini with a more elaborate prompt."""
    global _configured
    if not _configured:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set")
        genai.configure(api_key=api_key)
        _configured = True

    prompt = QUALITY_PROMPT.format(
        signature=alert["signature"],
        src_ip=alert["src_ip"],
        dest_ip=alert["dest_ip"],
        dest_port=alert["dest_port"],
        protocol=alert["protocol"],
    )

    start = time.perf_counter()
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        raw = response.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = json.loads(raw)
        severity = parsed.get("severity", "medium")
        attack_type = parsed.get("attack_type", "other")
        note = parsed.get("confidence_note", "")
    except Exception as e:
        print(f"[benchmark] Gemini quality-tier call failed: {e}")
        severity, attack_type, note = "medium", "other", "fallback - call failed"

    latency_ms = (time.perf_counter() - start) * 1000
    return {
        "severity": severity,
        "attack_type": attack_type,
        "confidence_note": note,
        "latency_ms": round(latency_ms, 1),
    }


def run_benchmark(alert: dict) -> dict:
    """Returns both tiers' results side by side for the same alert."""
    fast_result = classify_alert(alert)
    quality_result = _classify_quality_tier(alert)

    return {
        "alert": {"signature": alert["signature"], "src_ip": alert["src_ip"]},
        "fast_tier": {
            "provider": "Groq (llama-3.1-8b-instant)",
            "severity": fast_result["severity"],
            "attack_type": fast_result["attack_type"],
            "latency_ms": fast_result["classify_latency_ms"],
        },
        "quality_tier": {
            "provider": "Gemini (gemini-1.5-flash)",
            "severity": quality_result["severity"],
            "attack_type": quality_result["attack_type"],
            "confidence_note": quality_result["confidence_note"],
            "latency_ms": quality_result["latency_ms"],
        },
    }
