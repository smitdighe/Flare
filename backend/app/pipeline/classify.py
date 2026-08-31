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


CLASSIFY_SYSTEM_PROMPT = """You are a security alert triage classifier. Given an IDS alert, respond with ONLY a JSON object, no other text:
{"severity": "low" | "medium" | "high", "attack_type": "port_scan" | "ddos" | "malware" | "sql_injection" | "brute_force" | "other"}

Use these exact rules:
- Nmap scan, port scan, VNC scan, RDP scan, reconnaissance -> severity "low", attack_type "port_scan"
- SSH on non-standard port -> severity "low", attack_type "port_scan"
- SYN flood, UDP flood, DDoS -> severity "high", attack_type "ddos"
- SQL injection, LFI, Apache Struts, attack_request uri -> severity "high", attack_type "sql_injection"
- Malware, trojan callback, Meterpreter, Cobalt Strike, Emotet, Trickbot, EternalBlue, PowerShell download, C&C activity -> severity "high", attack_type "malware"
- Brute force, rapid login attempts, RDP brute force -> severity "medium", attack_type "brute_force"
- DNS tunnel, suspicious DNS query, crypto mining -> severity "medium", attack_type "malware"
- Outbound C&C traffic, possible outbound C&C -> severity "high", attack_type "malware"
- When unsure -> severity "medium", attack_type "other"
"""

SIGNATURE_RULES = {
    "ET SCAN Possible Nmap User-Agent Observed": ("low", "port_scan"),
    "ET SCAN Nmap -SYN Scan Detected": ("low", "port_scan"),
    "ET POLICY SSH client on non-standard port": ("low", "port_scan"),
    "ET DOS Possible SYN Flood to Web Server": ("high", "ddos"),
    "ET DOS Possible UDP Flood Detected": ("high", "ddos"),
    "ET WEB_SERVER SQL Injection Attempt in URI": ("high", "sql_injection"),
    "ET WEB_SERVER SQL Injection Attempt via POST": ("high", "sql_injection"),
    "ET MALWARE Suspicious PowerShell Download Cradle": ("high", "malware"),
    "ET MALWARE Meterpreter/Reverse TCP Callback Detected": ("high", "malware"),
    "ET TROJAN Generic Trojan Callback Detected": ("high", "malware"),
    "ET TROJAN Cobalt Strike Beacon Activity": ("high", "malware"),
    "ET SCAN Suspicious Rapid Login Attempts": ("medium", "brute_force"),
    "ET POLICY Suspicious DNS Query to Newly Seen Domain": ("medium", "malware"),
    "ET POLICY Outbound Connection to Port 4444 (Possible Meterpreter)": ("high", "malware"),
    "ET HUNTER Possible DNS Tunnel Activity": ("medium", "malware"),
    "GPL ATTACK_REQUEST uri/html": ("high", "sql_injection"),
    "ET WEB_SERVER Possible LFI Attempt": ("high", "sql_injection"),
    "ET WEB_SERVER Apache Struts Exploitation Attempt": ("high", "sql_injection"),
    "ET POLICY CryptoMining Pool Connection": ("medium", "malware"),
    "ET EXPLOIT EternalBlue MS17-010 SMB RCE Detection": ("high", "malware"),
    "ET EXPLOIT SMB/CIFS Windows NT Create AndX Request - Possible EternalBlue": ("high", "malware"),
    "ET SCAN Potential VNC Scan 5900-5920": ("low", "port_scan"),
    "ET SCAN Potential RDP Scan 3389": ("low", "port_scan"),
    "ET POLICY Possible Outbound C&C Traffic": ("high", "malware"),
    "ET MALWARE Emotet C&C Activity": ("high", "malware"),
    "ET MALWARE Trickbot CnC Activity": ("high", "malware"),
}


def classify_alert(alert: dict) -> dict:
    """
    Returns {"severity": ..., "attack_type": ..., "classify_latency_ms": ...}
    Falls back to a safe default (medium/other) if the model call fails,
    so one bad API response never kills the whole pipeline.
    """
    signature = alert.get("signature", "")
    if signature in SIGNATURE_RULES:
        severity, attack_type = SIGNATURE_RULES[signature]
        return {
            "severity": severity,
            "attack_type": attack_type,
            "classify_latency_ms": 0.0,
        }

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
