"""
Slack notification sender.
"""
import os
import json
from typing import Optional
import requests


def send_slack(webhook_url: str, message: str, channel: Optional[str] = None) -> bool:
    if not webhook_url:
        print("[slack] No webhook URL provided, skipping")
        return False

    payload = {"text": message}
    if channel:
        payload["channel"] = channel

    try:
        resp = requests.post(
            webhook_url,
            json=payload,
            timeout=10,
        )
        if resp.status_code == 200:
            print(f"[slack] Sent: {message[:50]}...")
            return True
        print(f"[slack] Failed: HTTP {resp.status_code}")
        return False
    except Exception as e:
        print(f"[slack] Error: {e}")
        return False


def format_alert_notification(alert: dict) -> str:
    severity = alert.get("severity", "unknown")
    emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(severity, "⚪")
    return (
        f"{emoji} *[{severity.upper()}]* Alert: {alert.get('signature', 'Unknown')}\n"
        f"Source: {alert.get('src_ip', '?')} → {alert.get('dest_ip', '?')}:{alert.get('dest_port', '?')}\n"
        f"Attack Type: {alert.get('attack_type', 'unknown')}\n"
        f"MITRE: {alert.get('mitre_technique', 'N/A')}"
    )
