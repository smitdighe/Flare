"""
Stage 1 of the Flare pipeline: fast-pass classification.

Takes a raw alert, asks Groq (fast model) to tag severity + attack type
in one short structured call. This is the "sort emergency calls" step -
it must be cheap and quick, because every single alert goes through it.
"""
import json
import os
import time

from groq import Groq

_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set - copy .env.example to .env and fill it in")
        _client = Groq(api_key=api_key)
    return _client


CLASSIFY_SYSTEM_PROMPT = """You are a fast security alert triage classifier.
Given a single IDS alert (signature text, src/dest IP, port, protocol), respond
with ONLY a JSON object, no other text, in this exact shape:
{"severity": "low" | "medium" | "high", "attack_type": "port_scan" | "ddos" | "malware" | "sql_injection" | "brute_force" | "other"}

Guidance:
- port scans / reconnaissance signatures -> usually low or medium
- SYN floods, DDoS signatures -> high
- SQL injection, malware, trojan callbacks -> high
- brute force / rapid login attempts -> medium
- when genuinely unsure, prefer "medium" over guessing high or low
"""


def classify_alert(alert: dict) -> dict:
    """
    Returns {"severity": ..., "attack_type": ..., "classify_latency_ms": ...}
    Falls back to a safe default (medium/other) if the model call fails,
    so one bad API response never kills the whole pipeline.
    """
    client = _get_client()
    user_prompt = (
        f"Signature: {alert['signature']}\n"
        f"Source IP: {alert['src_ip']} -> Dest: {alert['dest_ip']}:{alert['dest_port']} ({alert['protocol']})"
    )

    start = time.perf_counter()
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": CLASSIFY_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=60,
        )
        raw = completion.choices[0].message.content.strip()
        parsed = json.loads(raw)
        severity = parsed.get("severity", "medium")
        attack_type = parsed.get("attack_type", "other")
    except Exception as e:
        print(f"[classify] Groq call failed, defaulting to medium/other: {e}")
        severity, attack_type = "medium", "other"

    latency_ms = (time.perf_counter() - start) * 1000
    return {
        "severity": severity,
        "attack_type": attack_type,
        "classify_latency_ms": round(latency_ms, 1),
    }
