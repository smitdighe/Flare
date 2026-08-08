"""
VirusTotal enrichment — IP and hash lookups.

Runs as part of stage 2 (enrichment) alongside AbuseIPDB. Rate-limited to
4 requests/minute on the free tier, so we handle 429s gracefully and fall
back to AbuseIPDB-only if VT is exhausted.
"""
import os
import time

import requests

VT_IP_URL = "https://www.virustotal.com/api/v3/ip_addresses/{ip}"
VT_HASH_URL = "https://www.virustotal.com/api/v3/files/{hash}"

_vt_last_call = 0.0
_VT_MIN_INTERVAL = 15.1


def _rate_limit():
    global _vt_last_call
    elapsed = time.time() - _vt_last_call
    if elapsed < _VT_MIN_INTERVAL:
        time.sleep(_VT_MIN_INTERVAL - elapsed)
    _vt_last_call = time.time()


def _check_ip_vt(ip: str) -> dict | None:
    api_key = os.environ.get("VIRUSTOTAL_API_KEY")
    if not api_key:
        return None
    _rate_limit()
    try:
        resp = requests.get(
            VT_IP_URL.format(ip=ip),
            headers={"x-apikey": api_key, "Accept": "application/json"},
            timeout=8,
        )
        if resp.status_code == 429:
            print("[enrich] VirusTotal rate limited on IP lookup")
            return None
        resp.raise_for_status()
        attrs = resp.json().get("data", {}).get("attributes", {})
        stats = attrs.get("last_analysis_stats", {})
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        total_engines = sum(stats.values()) if stats else 0
        return {
            "malicious_detections": malicious,
            "suspicious_detections": suspicious,
            "total_engines": total_engines,
            "reputation": attrs.get("reputation", 0),
            "country": attrs.get("country", ""),
            "as_owner": attrs.get("as_owner", ""),
            "tags": attrs.get("tags", []),
        }
    except Exception as e:
        print(f"[enrich] VirusTotal IP lookup failed for {ip}: {e}")
        return None


def _check_hash_vt(file_hash: str) -> dict | None:
    api_key = os.environ.get("VIRUSTOTAL_API_KEY")
    if not api_key:
        return None
    _rate_limit()
    try:
        resp = requests.get(
            VT_HASH_URL.format(hash=file_hash),
            headers={"x-apikey": api_key, "Accept": "application/json"},
            timeout=8,
        )
        if resp.status_code == 429:
            print("[enrich] VirusTotal rate limited on hash lookup")
            return None
        if resp.status_code == 404:
            return {"status": "not_found", "message": "File not yet in VirusTotal database"}
        resp.raise_for_status()
        attrs = resp.json().get("data", {}).get("attributes", {})
        stats = attrs.get("last_analysis_stats", {})
        malicious = stats.get("malicious", 0)
        total_engines = sum(stats.values()) if stats else 0
        return {
            "status": "found",
            "malicious_detections": malicious,
            "total_engines": total_engines,
            "names": attrs.get("names", [])[:3],
            "tags": attrs.get("tags", []),
            "reputation": attrs.get("reputation", 0),
        }
    except Exception as e:
        print(f"[enrich] VirusTotal hash lookup failed for {file_hash}: {e}")
        return None


def enrich_with_virustotal(alert: dict) -> dict:
    """
    Enriches an alert with VirusTotal data. Returns both IP and hash info
    if available. For alerts that imply file hashes (malware alerts), we
    generate a synthetic hash from the signature for demo purposes.
    """
    result = {"vt_ip": None, "vt_hash": None}

    src_ip = alert.get("src_ip")
    if src_ip:
        ip_data = _check_ip_vt(src_ip)
        if ip_data:
            if ip_data.get("malicious_detections", 0) > 0:
                result["vt_ip"] = (
                    f"Flagged malicious by {ip_data['malicious_detections']}/{ip_data['total_engines']} "
                    f"engines"
                    + (f", reputation: {ip_data['reputation']}" if ip_data.get("reputation") else "")
                    + (f", AS: {ip_data['as_owner']}" if ip_data.get("as_owner") else "")
                )
            elif ip_data.get("suspicious_detections", 0) > 0:
                result["vt_ip"] = (
                    f"Flagged suspicious by {ip_data['suspicious_detections']}/{ip_data['total_engines']} engines"
                )
            else:
                result["vt_ip"] = f"Clean — 0/{ip_data.get('total_engines', 0)} engines flagged"

    severity = alert.get("severity", "low")
    attack_type = alert.get("attack_type", "")
    if severity in ("medium", "high") and attack_type in ("malware", "sql_injection"):
        import hashlib
        sig = alert.get("signature", "")
        synthetic_hash = hashlib.md5(sig.encode()).hexdigest()
        hash_data = _check_hash_vt(synthetic_hash)
        if hash_data:
            if hash_data.get("status") == "not_found":
                result["vt_hash"] = f"Hash {synthetic_hash[:12]}... not yet in VirusTotal database"
            elif hash_data.get("malicious_detections", 0) > 0:
                result["vt_hash"] = (
                    f"Malware detected by {hash_data['malicious_detections']}/{hash_data['total_engines']} "
                    f"engines"
                    + (f" — tags: {', '.join(hash_data['tags'][:3])}" if hash_data.get("tags") else "")
                )
            else:
                result["vt_hash"] = f"Clean — 0/{hash_data.get('total_engines', 0)} engines flagged"

    return result
