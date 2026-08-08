"""
API key health checker. Tests each external API key on demand and reports
whether it's configured, valid, and rate-limited — displayed on the dashboard
so judges always know the live state of integrations.

Results are cached for 60 seconds to avoid burning free-tier API quotas
when the frontend polls the health endpoint.
"""
import os
import time

import requests

_CACHE: dict = {}
_CACHE_TTL: int = 60  # seconds


def check_groq() -> dict:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return {"name": "Groq", "status": "not_configured", "message": "GROQ_API_KEY not set"}
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        start = time.time()
        client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Say OK"}],
            max_tokens=3,
        )
        latency = round((time.time() - start) * 1000)
        return {"name": "Groq", "status": "ok", "message": f"llama-3.1-8b-instant responding", "latency_ms": latency}
    except Exception as e:
        msg = str(e)
        if "429" in msg or "rate" in msg.lower():
            return {"name": "Groq", "status": "rate_limited", "message": "Rate limited — retry shortly"}
        return {"name": "Groq", "status": "error", "message": msg[:120]}


def check_gemini() -> dict:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"name": "Gemini", "status": "not_configured", "message": "GEMINI_API_KEY not set"}
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        start = time.time()
        model.generate_content("Say OK")
        latency = round((time.time() - start) * 1000)
        return {"name": "Gemini", "status": "ok", "message": "gemini-1.5-flash responding", "latency_ms": latency}
    except Exception as e:
        msg = str(e)
        if "429" in msg or "quota" in msg.lower() or "rate" in msg.lower():
            return {"name": "Gemini", "status": "rate_limited", "message": "Rate limited — retry shortly"}
        return {"name": "Gemini", "status": "error", "message": msg[:120]}


def check_abuseipdb() -> dict:
    api_key = os.environ.get("ABUSEIPDB_API_KEY")
    if not api_key:
        return {"name": "AbuseIPDB", "status": "not_configured", "message": "ABUSEIPDB_API_KEY not set"}
    try:
        start = time.time()
        resp = requests.get(
            "https://api.abuseipdb.com/api/v2/check",
            headers={"Key": api_key, "Accept": "application/json"},
            params={"ipAddress": "8.8.8.8", "maxAgeInDays": 1},
            timeout=5,
        )
        latency = round((time.time() - start) * 1000)
        if resp.status_code == 200:
            return {"name": "AbuseIPDB", "status": "ok", "message": "API responding", "latency_ms": latency}
        if resp.status_code == 429:
            return {"name": "AbuseIPDB", "status": "rate_limited", "message": "Rate limited — 1000 req/day free tier"}
        return {"name": "AbuseIPDB", "status": "error", "message": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"name": "AbuseIPDB", "status": "error", "message": str(e)[:120]}


def check_virustotal() -> dict:
    api_key = os.environ.get("VIRUSTOTAL_API_KEY")
    if not api_key:
        return {"name": "VirusTotal", "status": "not_configured", "message": "VIRUSTOTAL_API_KEY not set"}
    try:
        start = time.time()
        resp = requests.get(
            "https://www.virustotal.com/api/v3/ip_addresses/8.8.8.8",
            headers={"x-apikey": api_key, "Accept": "application/json"},
            timeout=8,
        )
        latency = round((time.time() - start) * 1000)
        if resp.status_code == 200:
            return {"name": "VirusTotal", "status": "ok", "message": "API responding", "latency_ms": latency}
        if resp.status_code == 429:
            return {"name": "VirusTotal", "status": "rate_limited", "message": "Rate limited — 4 req/min free tier"}
        return {"name": "VirusTotal", "status": "error", "message": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"name": "VirusTotal", "status": "error", "message": str(e)[:120]}


def check_all() -> dict:
    now = time.time()
    if _CACHE.get("data") and (now - _CACHE.get("ts", 0)) < _CACHE_TTL:
        return _CACHE["data"]
    result = {
        "services": [
            check_groq(),
            check_gemini(),
            check_abuseipdb(),
            check_virustotal(),
        ]
    }
    _CACHE["data"] = result
    _CACHE["ts"] = now
    return result
