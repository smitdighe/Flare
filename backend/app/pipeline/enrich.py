"""
Stage 2 of the pipeline: IOC enrichment.

Runs AbuseIPDB (IP reputation) AND VirusTotal (IP + hash reputation) for
medium/high severity alerts. Low severity alerts skip enrichment entirely
to save API quota on free tiers.
"""
import os
import time

import requests

from app.pipeline.virustotal import enrich_with_virustotal

ABUSEIPDB_URL = "https://api.abuseipdb.com/api/v2/check"


def _check_abuseipdb(ip: str) -> dict | None:
    api_key = os.environ.get("ABUSEIPDB_API_KEY")
    if not api_key:
        return None
    try:
        resp = requests.get(
            ABUSEIPDB_URL,
            headers={"Key": api_key, "Accept": "application/json"},
            params={"ipAddress": ip, "maxAgeInDays": 90},
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json().get("data", {})
        return {
            "abuse_score": data.get("abuseConfidenceScore", 0),
            "total_reports": data.get("totalReports", 0),
            "country": data.get("countryCode"),
            "is_known_attacker": data.get("abuseConfidenceScore", 0) >= 50,
        }
    except Exception as e:
        print(f"[enrich] AbuseIPDB lookup failed for {ip}: {e}")
        return None


def enrich_alert(alert: dict) -> dict:
    start = time.perf_counter()
    severity = alert.get("severity", "medium")

    if severity == "low":
        return {
            "ioc_reputation": None,
            "ioc_checked": False,
            "enrich_latency_ms": 0.0,
            "vt_ip": None,
            "vt_hash": None,
        }

    src_ip = alert.get("src_ip")
    abuse_result = _check_abuseipdb(src_ip) if src_ip else None

    if abuse_result is None:
        reputation = "Reputation lookup unavailable (API error or rate limit) - treat as unverified."
    elif abuse_result["is_known_attacker"]:
        reputation = (
            f"Known malicious - {abuse_result['abuse_score']}% abuse confidence, "
            f"{abuse_result['total_reports']} prior reports"
            + (f", origin {abuse_result['country']}" if abuse_result.get("country") else "")
        )
    elif abuse_result["total_reports"] > 0:
        reputation = (
            f"Some history - {abuse_result['abuse_score']}% abuse confidence, "
            f"{abuse_result['total_reports']} prior reports, not yet flagged as malicious"
        )
    else:
        reputation = "No prior reports found - not currently known malicious"

    vt_data = enrich_with_virustotal(alert)

    latency_ms = (time.perf_counter() - start) * 1000
    return {
        "ioc_reputation": reputation,
        "ioc_checked": True,
        "enrich_latency_ms": round(latency_ms, 1),
        "vt_ip": vt_data.get("vt_ip"),
        "vt_hash": vt_data.get("vt_hash"),
    }
