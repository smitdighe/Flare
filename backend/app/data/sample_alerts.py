"""
Day-1 stand-in for the real CICIDS2017 / Suricata EVE JSON replay.
Generates realistic-looking alerts so the pipeline + dashboard can run
end-to-end before the real dataset loader is wired in.

Swap this out later for a real file reader (see data/replay_loader.py, added Day 2).
"""
import random
import uuid
from datetime import datetime, timezone

SIGNATURES = [
    "ET SCAN Possible Nmap User-Agent Observed",
    "ET POLICY SSH client on non-standard port",
    "ET DOS Possible SYN Flood to Web Server",
    "ET WEB_SERVER SQL Injection Attempt in URI",
    "ET MALWARE Suspicious PowerShell Download",
    "ET SCAN Suspicious Rapid Login Attempts",
    "ET TROJAN Generic Trojan Callback Detected",
    "ET POLICY Suspicious DNS Query to Newly Seen Domain",
]

# Ground truth labels for the eval panel later — kept alongside so we can
# score the pipeline's guesses against something.
GROUND_TRUTH = {
    "ET SCAN Possible Nmap User-Agent Observed": ("low", "port_scan"),
    "ET POLICY SSH client on non-standard port": ("low", "port_scan"),
    "ET DOS Possible SYN Flood to Web Server": ("high", "ddos"),
    "ET WEB_SERVER SQL Injection Attempt in URI": ("high", "sql_injection"),
    "ET MALWARE Suspicious PowerShell Download": ("high", "malware"),
    "ET SCAN Suspicious Rapid Login Attempts": ("medium", "brute_force"),
    "ET TROJAN Generic Trojan Callback Detected": ("high", "malware"),
    "ET POLICY Suspicious DNS Query to Newly Seen Domain": ("medium", "malware"),
}

KNOWN_BAD_IPS = ["45.155.204.113", "185.220.101.45", "194.165.16.72"]

ENRICHED_SIGNATURES = list(GROUND_TRUTH.keys())


def make_fake_alert() -> dict:
    signature = random.choice(SIGNATURES)
    src_ip = (
        random.choice(KNOWN_BAD_IPS)
        if random.random() < 0.35
        else f"{random.randint(10,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    )
    return {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "src_ip": src_ip,
        "dest_ip": f"10.0.{random.randint(0,10)}.{random.randint(1,254)}",
        "dest_port": random.choice([22, 80, 443, 3389, 445, 8080]),
        "protocol": random.choice(["TCP", "UDP"]),
        "signature": signature,
    }
