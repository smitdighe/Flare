"""
Eval harness: runs the real classification pipeline against 24 labeled
ground-truth alerts and computes precision/recall with a confusion matrix.
Refreshed live whenever a judge asks to see it.
"""
import uuid
from datetime import datetime, timezone

from app.data.sample_alerts import GROUND_TRUTH, KNOWN_BAD_IPS, ENRICHED_SIGNATURES
from app.pipeline.classify import classify_alert


GROUND_TRUTH_EXPANDED = {
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


def _build_labeled_alert(signature: str, true_severity: str, true_attack_type: str) -> dict:
    return {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "src_ip": KNOWN_BAD_IPS[0],
        "dest_ip": "10.0.0.5",
        "dest_port": 443,
        "protocol": "TCP",
        "signature": signature,
        "_true_severity": true_severity,
        "_true_attack_type": true_attack_type,
    }


def _build_confusion_matrix(rows: list[dict]) -> dict:
    labels = ["low", "medium", "high"]
    matrix = {f"{t}_vs_{p}": 0 for t in labels for p in labels}
    for r in rows:
        key = f"{r['true_severity']}_vs_{r['pred_severity']}"
        matrix[key] = matrix.get(key, 0) + 1

    result = {"labels": labels, "matrix": []}
    for t in labels:
        row = []
        for p in labels:
            row.append(matrix.get(f"{t}_vs_{p}", 0))
        result["matrix"].append(row)
    return result


def run_eval() -> dict:
    labeled_alerts = [
        _build_labeled_alert(sig, sev, atype) for sig, (sev, atype) in GROUND_TRUTH_EXPANDED.items()
    ]

    rows = []
    for alert in labeled_alerts:
        prediction = classify_alert(alert)
        rows.append({
            "signature": alert["signature"],
            "true_severity": alert["_true_severity"],
            "pred_severity": prediction["severity"],
            "true_attack_type": alert["_true_attack_type"],
            "pred_attack_type": prediction["attack_type"],
            "latency_ms": prediction["classify_latency_ms"],
        })

    total = len(rows)
    severity_correct = sum(1 for r in rows if r["pred_severity"] == r["true_severity"])
    attack_type_correct = sum(1 for r in rows if r["pred_attack_type"] == r["true_attack_type"])

    true_high = [r for r in rows if r["true_severity"] == "high"]
    pred_high = [r for r in rows if r["pred_severity"] == "high"]
    true_positive_high = sum(1 for r in rows if r["true_severity"] == "high" and r["pred_severity"] == "high")

    precision = round(true_positive_high / len(pred_high), 3) if pred_high else None
    recall = round(true_positive_high / len(true_high), 3) if true_high else None

    f1 = None
    if precision is not None and recall is not None and (precision + recall) > 0:
        f1 = round(2 * precision * recall / (precision + recall), 3)

    confusion = _build_confusion_matrix(rows)

    atk_labels = list(set(r["true_attack_type"] for r in rows))
    atk_confusion = {}
    for atk in atk_labels:
        true_atk = [r for r in rows if r["true_attack_type"] == atk]
        tp = sum(1 for r in true_atk if r["pred_attack_type"] == atk)
        atk_confusion[atk] = {
            "true_count": len(true_atk),
            "correct": tp,
            "accuracy": round(tp / len(true_atk), 3) if true_atk else 0,
        }

    misclassified = [r for r in rows if r["pred_severity"] != r["true_severity"] or r["pred_attack_type"] != r["true_attack_type"]]

    return {
        "sample_size": total,
        "severity_accuracy": round(severity_correct / total, 3),
        "attack_type_accuracy": round(attack_type_correct / total, 3),
        "high_severity_precision": precision,
        "high_severity_recall": recall,
        "high_severity_f1": f1,
        "avg_latency_ms": round(sum(r["latency_ms"] for r in rows) / total, 1),
        "confusion_matrix": confusion,
        "attack_type_breakdown": atk_confusion,
        "misclassified_count": len(misclassified),
        "rows": rows,
    }
