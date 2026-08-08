"""
CSV export generator.
"""
import csv
import io
from typing import List


def generate_csv(alerts: List[dict]) -> str:
    if not alerts:
        return ""

    output = io.StringIO()
    fieldnames = [
        "id", "timestamp", "src_ip", "dest_ip", "dest_port", "protocol",
        "signature", "severity", "attack_type", "mitre_technique",
        "ioc_checked", "ioc_reputation", "explanation",
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for alert in alerts:
        writer.writerow(alert)

    return output.getvalue()
