"""
CICIDS2017 dataset loader. Loads a pre-processed subset of the CICIDS2017
intrusion detection dataset and replays alerts from it instead of using
the fake generator.

If no CSV file is found, falls back to an expanded synthetic dataset
that mimics CICIDS2017 traffic patterns.
"""
import csv
import os
import random
import uuid
from datetime import datetime, timezone, timedelta

CICIDS_SIGNATURE_MAP = {
    "BENIGN": ("low", "other"),
    "DoS Hulk": ("high", "ddos"),
    "DoS GoldenEye": ("high", "ddos"),
    "DoS slowloris": ("medium", "ddos"),
    "DoS Slowhttptest": ("medium", "ddos"),
    "DDoS": ("high", "ddos"),
    "PortScan": ("low", "port_scan"),
    "FTP-Patator": ("medium", "brute_force"),
    "SSH-Patator": ("medium", "brute_force"),
    "Web Attack - Brute Force": ("high", "brute_force"),
    "Web Attack - XSS": ("high", "sql_injection"),
    "Web Attack - SQL Injection": ("high", "sql_injection"),
    "Infiltration": ("high", "malware"),
    "Bot": ("medium", "malware"),
    "Heartbleed": ("high", "malware"),
}

ENRICHED_SIGNATURES = [
    ("ET SCAN Possible Nmap User-Agent Observed", "low", "port_scan"),
    ("ET SCAN Nmap -SYN Scan Detected", "low", "port_scan"),
    ("ET POLICY SSH client on non-standard port", "low", "port_scan"),
    ("ET DOS Possible SYN Flood to Web Server", "high", "ddos"),
    ("ET DOS Possible UDP Flood Detected", "high", "ddos"),
    ("ET WEB_SERVER SQL Injection Attempt in URI", "high", "sql_injection"),
    ("ET WEB_SERVER SQL Injection Attempt via POST", "high", "sql_injection"),
    ("ET MALWARE Suspicious PowerShell Download Cradle", "high", "malware"),
    ("ET MALWARE Meterpreter/Reverse TCP Callback Detected", "high", "malware"),
    ("ET TROJAN Generic Trojan Callback Detected", "high", "malware"),
    ("ET TROJAN Cobalt Strike Beacon Activity", "high", "malware"),
    ("ET SCAN Suspicious Rapid Login Attempts", "medium", "brute_force"),
    ("ET POLICY Suspicious DNS Query to Newly Seen Domain", "medium", "malware"),
    ("ET POLICY Outbound Connection to Port 4444 (Possible Meterpreter)", "high", "malware"),
    ("ET HUNTER Possible DNS Tunnel Activity", "medium", "malware"),
    ("GPL ATTACK_REQUEST uri/html", "high", "sql_injection"),
    ("ET WEB_SERVER Possible LFI Attempt", "high", "sql_injection"),
    ("ET WEB_SERVER Apache Struts Exploitation Attempt", "high", "sql_injection"),
    ("ET INFO Session Traversal Utilities for NAT (STUN)", "low", "other"),
    ("ET POLICY CryptoMining Pool Connection", "medium", "malware"),
    ("ET EXPLOIT EternalBlue MS17-010 SMB RCE Detection", "high", "malware"),
    ("ET EXPLOIT SMB/CIFS Windows NT Create AndX Request - Possible EternalBlue", "high", "malware"),
    ("ET SCAN Potential VNC Scan 5900-5920", "low", "port_scan"),
    ("ET SCAN Potential RDP Scan 3389", "low", "port_scan"),
    ("ET POLICY Possible Outbound C&C Traffic", "high", "malware"),
    ("ET MALWARE Emotet C&C Activity", "high", "malware"),
    ("ET MALWARE Trickbot CnC Activity", "high", "malware"),
    ("ET MALWARE Emotet Epoch4 C&C Activity", "high", "malware"),
    ("ET WEB_SERVER PHP Remote File Inclusion Attempt", "high", "sql_injection"),
    ("ET WEB_SERVER JBoss Deserialization Remote Code Execution Attempt", "high", "sql_injection"),
]

KNOWN_BAD_IPS = [
    "45.155.204.113", "185.220.101.45", "194.165.16.72",
    "141.98.10.63", "91.219.237.1", "185.220.100.252",
    "23.129.64.100", "176.126.252.11", "103.214.150.88",
    "45.33.32.156", "198.51.100.1", "203.0.113.42",
    "89.248.167.131", "141.98.10.232", "77.247.181.162",
]

KNOWN_GOOD_IPS = [
    "8.8.8.8", "1.1.1.1", "208.67.222.222", "9.9.9.9",
    "185.125.190.36", "151.101.1.140", "140.82.121.3",
    "52.96.108.18", "13.107.42.14", "20.190.159.0",
]

INTERNAL_IPS = [f"10.0.{random.randint(0,10)}.{random.randint(1,254)}" for _ in range(30)]


def _random_cicids_type() -> str:
    weights = [
        ("BENIGN", 35), ("DoS Hulk", 8), ("DDoS", 8), ("PortScan", 15),
        ("FTP-Patator", 4), ("SSH-Patator", 4), ("Web Attack - Brute Force", 5),
        ("Web Attack - XSS", 3), ("Web Attack - SQL Injection", 3),
        ("DoS GoldenEye", 3), ("Infiltration", 3), ("Bot", 4),
        ("DoS slowloris", 2), ("Heartbleed", 1),
    ]
    names, w = zip(*weights)
    return random.choices(names, weights=w, k=1)[0]


def make_cicids_alert() -> dict:
    cicids_type = _random_cicids_type()
    severity, attack_type = CICIDS_SIGNATURE_MAP.get(cicids_type, ("medium", "other"))

    sig_entry = random.choice(ENRICHED_SIGNATURES)
    if cicids_type != "BENIGN":
        signature = f"CICIDS:{cicids_type} — {sig_entry[0]}"
    else:
        signature = sig_entry[0]

    if severity == "low" and random.random() < 0.4:
        severity = "medium"

    src_ip = (
        random.choice(KNOWN_BAD_IPS)
        if random.random() < 0.3
        else random.choice(KNOWN_GOOD_IPS)
        if random.random() < 0.5
        else f"{random.randint(10,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    )

    now = datetime.now(timezone.utc)
    offset_ms = random.randint(0, 60000)
    ts = (now - timedelta(milliseconds=offset_ms)).isoformat()

    return {
        "id": str(uuid.uuid4())[:8],
        "timestamp": ts,
        "src_ip": src_ip,
        "dest_ip": random.choice(INTERNAL_IPS),
        "dest_port": random.choice([22, 80, 443, 3389, 445, 8080, 8443, 3306, 5432, 53]),
        "protocol": random.choice(["TCP", "UDP", "TCP"]),
        "signature": signature,
    }


def load_cicids_csv(filepath: str) -> list[dict]:
    alerts = []
    if not os.path.exists(filepath):
        return alerts
    try:
        with open(filepath, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                label = row.get("Label", "BENIGN").strip()
                severity, attack_type = CICIDS_SIGNATURE_MAP.get(label, ("low", "other"))
                alerts.append({
                    "id": str(uuid.uuid4())[:8],
                    "timestamp": row.get("Timestamp", datetime.now(timezone.utc).isoformat()),
                    "src_ip": row.get("Source IP", f"{random.randint(10,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"),
                    "dest_ip": row.get("Destination IP", random.choice(INTERNAL_IPS)),
                    "dest_port": int(row.get("Destination Port", 80)),
                    "protocol": row.get("Protocol", "TCP"),
                    "signature": f"CICIDS:{label}",
                })
    except Exception as e:
        print(f"[data] Failed to load CICIDS CSV: {e}")
    return alerts[:500]
