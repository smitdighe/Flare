"""
Notification dispatcher: fan-out to all configured channels.
"""
import json
from typing import Optional
from sqlalchemy.orm import Session

from app.models_db import NotificationPreference, NotificationLog, User
from app.notifications.email import send_email
from app.notifications.slack import send_slack, format_alert_notification


def dispatch_notification(
    db: Session,
    event_type: str,
    subject: str,
    body: str,
    user_id: Optional[str] = None,
    alert_data: Optional[dict] = None,
):
    query = db.query(NotificationPreference).filter(
        NotificationPreference.event_type == event_type,
        NotificationPreference.is_enabled == True,
    )
    if user_id:
        query = query.filter(NotificationPreference.user_id == user_id)

    prefs = query.all()
    for pref in prefs:
        user = db.query(User).filter(User.id == pref.user_id).first()
        if not user:
            continue

        config = json.loads(pref.config) if pref.config else {}
        status = "pending"
        error = None

        if pref.channel == "email":
            email = config.get("email") or user.email
            success = send_email(email, subject, body)
            status = "sent" if success else "failed"
            if not success:
                error = "Email send failed"
        elif pref.channel == "slack":
            webhook = config.get("webhook_url", "")
            success = send_slack(webhook, body)
            status = "sent" if success else "failed"
            if not success:
                error = "Slack send failed"

        log = NotificationLog(
            user_id=pref.user_id,
            channel=pref.channel,
            event_type=event_type,
            subject=subject,
            status=status,
            error_message=error,
        )
        db.add(log)

    db.commit()


def notify_high_severity_alert(db: Session, alert: dict):
    subject = f"[HIGH] Flare Alert: {alert.get('signature', 'Unknown')}"
    body = format_alert_notification(alert)
    dispatch_notification(db, "alert.high_severity", subject, body, alert_data=alert)
