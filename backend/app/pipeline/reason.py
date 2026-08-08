"""
Stage 3 of the pipeline: deep reasoning.

Only runs for medium/high severity alerts. Retrieves the most relevant
MITRE ATT&CK technique(s) via the RAG retriever, then asks Gemini to explain
the attack and recommend remediation *grounded in that retrieved context*
rather than from memory alone - this is the actual RAG step, not just an
LLM call with "MITRE" mentioned in the prompt.
"""
import json
import os
import time

import google.generativeai as genai

from app.rag.retriever import retrieve_technique

_configured = False


def _ensure_configured():
    global _configured
    if not _configured:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set - copy .env.example to .env and fill it in")
        genai.configure(api_key=api_key)
        _configured = True


REASON_PROMPT_TEMPLATE = """You are a security analyst assistant. Given an alert and relevant
MITRE ATT&CK technique context retrieved from a knowledge base, explain what happened in plain
English and recommend concrete remediation steps.

Ground your explanation in the retrieved technique(s) below - reference the technique ID and
name naturally in your explanation. Do not invent a technique that isn't in the retrieved context.

Respond with ONLY a JSON object, no other text, in this exact shape:
{{"explanation": "2-3 sentences: what happened, why, and how this technique typically works",
"mitre_technique": "T#### - Technique Name",
"remediation": ["step 1", "step 2", "step 3", "step 4"]}}

ALERT:
Signature: {signature}
Attack type: {attack_type}
Severity: {severity}
Source: {src_ip} -> {dest_ip}:{dest_port}
IOC reputation: {ioc_reputation}

RETRIEVED MITRE CONTEXT:
{mitre_context}
"""


def reason_about_alert(alert: dict) -> dict:
    """
    Returns {"explanation": str, "mitre_technique": str, "remediation": list[str],
    "reasoning_latency_ms": float}
    """
    start = time.perf_counter()
    severity = alert.get("severity", "medium")

    if severity == "low":
        return {
            "explanation": None,
            "mitre_technique": None,
            "remediation": None,
            "reasoning_latency_ms": 0.0,
        }

    techniques = retrieve_technique(alert, top_k=2)
    mitre_context = "\n\n".join(
        f"{t['id']} - {t['name']}: {t['description']}\nTypical remediation: {', '.join(t['remediation'])}"
        for t in techniques
    ) or "No specific technique retrieved - reason generally about this attack type."

    prompt = REASON_PROMPT_TEMPLATE.format(
        signature=alert.get("signature", ""),
        attack_type=alert.get("attack_type", ""),
        severity=severity,
        src_ip=alert.get("src_ip", ""),
        dest_ip=alert.get("dest_ip", ""),
        dest_port=alert.get("dest_port", ""),
        ioc_reputation=alert.get("ioc_reputation") or "not checked",
        mitre_context=mitre_context,
    )

    try:
        _ensure_configured()
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        raw = response.text.strip()
        # Gemini sometimes wraps JSON in markdown fences despite instructions
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = json.loads(raw)
        explanation = parsed.get("explanation")
        mitre_technique = parsed.get("mitre_technique")
        remediation = parsed.get("remediation")
    except Exception as e:
        print(f"[reason] Gemini call failed, falling back to retrieved technique directly: {e}")
        top = techniques[0] if techniques else None
        if top and "name" in top:
            explanation = f"This alert matches the pattern of {top['name']} ({top.get('id', 'unknown')})."
            mitre_technique = f"{top.get('id', 'unknown')} - {top['name']}"
            remediation = top.get("remediation", ["Investigate manually."])
        else:
            explanation = "Unable to generate a detailed explanation for this alert right now."
            mitre_technique = None
            remediation = ["Investigate manually - automated reasoning unavailable."]

    latency_ms = (time.perf_counter() - start) * 1000
    return {
        "explanation": explanation,
        "mitre_technique": mitre_technique,
        "remediation": remediation,
        "reasoning_latency_ms": round(latency_ms, 1),
    }
