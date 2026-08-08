"""
SQL-backed alert store. Replaces the in-memory store with SQLite persistence.
Maintains the same public API so existing endpoints work unchanged.
"""
import json
import threading
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models_db import Alert


class AlertStore:
    def __init__(self, max_size: int = 500):
        self._lock = threading.Lock()
        self._max_size = max_size

    def _get_db(self) -> Session:
        return SessionLocal()

    def append(self, alert: dict):
        db = self._get_db()
        try:
            ts = alert.get("timestamp", "")
            if isinstance(ts, str) and ts:
                try:
                    ts_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                except ValueError:
                    ts_dt = datetime.now(timezone.utc)
            elif isinstance(ts, datetime):
                ts_dt = ts
            else:
                ts_dt = datetime.now(timezone.utc)

            remediation = alert.get("remediation")
            if isinstance(remediation, list):
                remediation = json.dumps(remediation)

            db_alert = Alert(
                id=alert.get("id", ""),
                user_id=alert.get("user_id"),
                timestamp=ts_dt,
                src_ip=alert.get("src_ip", ""),
                dest_ip=alert.get("dest_ip", ""),
                dest_port=alert.get("dest_port", 0),
                protocol=alert.get("protocol", ""),
                signature=alert.get("signature", ""),
                severity=alert.get("severity"),
                attack_type=alert.get("attack_type"),
                ioc_reputation=alert.get("ioc_reputation"),
                ioc_checked=alert.get("ioc_checked", False),
                vt_ip=alert.get("vt_ip"),
                vt_hash=alert.get("vt_hash"),
                mitre_technique=alert.get("mitre_technique"),
                explanation=alert.get("explanation"),
                remediation=remediation,
                classify_latency_ms=alert.get("classify_latency_ms"),
                enrich_latency_ms=alert.get("enrich_latency_ms"),
                reasoning_latency_ms=alert.get("reasoning_latency_ms"),
            )
            db.merge(db_alert)
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def count(self) -> int:
        db = self._get_db()
        try:
            return db.query(Alert).count()
        finally:
            db.close()

    def get_by_id(self, alert_id: str) -> Optional[dict]:
        db = self._get_db()
        try:
            alert = db.query(Alert).filter(Alert.id == alert_id).first()
            return alert.to_dict() if alert else None
        finally:
            db.close()

    def filter(
        self,
        severity: Optional[str] = None,
        attack_type: Optional[str] = None,
        search: Optional[str] = None,
        min_severity: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        sev_order = {"low": 0, "medium": 1, "high": 2}
        db = self._get_db()
        try:
            query = db.query(Alert)

            if severity:
                query = query.filter(Alert.severity == severity)
            if attack_type:
                query = query.filter(Alert.attack_type == attack_type)
            if min_severity:
                min_val = sev_order.get(min_severity, 0)
                valid_sevs = [s for s, v in sev_order.items() if v >= min_val]
                query = query.filter(Alert.severity.in_(valid_sevs))
            if search:
                q = f"%{search}%"
                query = query.filter(
                    Alert.signature.ilike(q)
                    | Alert.src_ip.ilike(q)
                    | Alert.dest_ip.ilike(q)
                    | Alert.id.ilike(q)
                )

            total = query.count()
            alerts = query.order_by(Alert.created_at.desc()).offset(offset).limit(limit).all()
            return {
                "alerts": [a.to_dict() for a in alerts],
                "total": total,
                "offset": offset,
                "limit": limit,
            }
        finally:
            db.close()

    def top_offending_ips(self, limit: int = 10) -> list[dict]:
        db = self._get_db()
        try:
            alerts = db.query(Alert).all()
            by_src = defaultdict(lambda: {"count": 0, "severities": [], "types": set()})
            for a in alerts:
                src = a.src_ip
                if src:
                    by_src[src]["count"] += 1
                    by_src[src]["severities"].append(a.severity or "low")
                    by_src[src]["types"].add(a.attack_type or "unknown")

            sev_weight = {"high": 3, "medium": 2, "low": 1}
            ranked = sorted(
                by_src.items(),
                key=lambda x: sum(sev_weight.get(s, 0) for s in x[1]["severities"]),
                reverse=True,
            )
            return [
                {
                    "ip": ip,
                    "alert_count": data["count"],
                    "threat_score": sum(sev_weight.get(s, 0) for s in data["severities"]),
                    "attack_types": list(data["types"]),
                }
                for ip, data in ranked[:limit]
            ]
        finally:
            db.close()

    def alert_velocity(self, minutes: int = 5) -> float:
        db = self._get_db()
        try:
            cutoff = datetime.now(timezone.utc).timestamp() - (minutes * 60)
            count = 0
            for a in db.query(Alert).all():
                if a.timestamp and a.timestamp.timestamp() >= cutoff:
                    count += 1
            return round(count / max(minutes, 1), 2)
        finally:
            db.close()

    def success_rate(self) -> float:
        db = self._get_db()
        try:
            total = db.query(Alert).count()
            if not total:
                return 0.0
            completed = db.query(Alert).filter(Alert.severity.isnot(None)).filter(Alert.classify_latency_ms.isnot(None)).count()
            return round(completed / total * 100, 1)
        finally:
            db.close()

    def stats(self) -> dict:
        db = self._get_db()
        try:
            alerts = db.query(Alert).all()
            if not alerts:
                return {
                    "total": 0,
                    "by_severity": {"low": 0, "medium": 0, "high": 0},
                    "by_attack_type": {},
                    "avg_classify_ms": 0,
                    "avg_enrich_ms": 0,
                    "avg_reason_ms": 0,
                    "avg_total_ms": 0,
                    "ioc_checked_pct": 0,
                    "reasoned_pct": 0,
                    "unique_src_ips": 0,
                    "unique_dst_ips": 0,
                    "timeline": [],
                    "top_offending_ips": [],
                    "alert_velocity": 0.0,
                    "pipeline_success_rate": 0.0,
                }

            by_sev = defaultdict(int)
            by_atk = defaultdict(int)
            total_classify = 0
            total_enrich = 0
            total_reason = 0
            ioc_count = 0
            reason_count = 0
            src_ips = set()
            dst_ips = set()
            timeline_buckets = defaultdict(int)

            for a in alerts:
                sev = a.severity or "unknown"
                atk = a.attack_type or "unknown"
                by_sev[sev] += 1
                by_atk[atk] += 1
                total_classify += a.classify_latency_ms or 0
                total_enrich += a.enrich_latency_ms or 0
                total_reason += a.reasoning_latency_ms or 0
                if a.ioc_checked:
                    ioc_count += 1
                if a.explanation:
                    reason_count += 1
                src_ips.add(a.src_ip)
                dst_ips.add(a.dest_ip)
                if a.timestamp:
                    bucket = a.timestamp.strftime("%Y-%m-%dT%H:%M")
                    timeline_buckets[bucket] += 1

            n = len(alerts)
            timeline = sorted(
                [{"time": k, "count": v} for k, v in timeline_buckets.items()],
                key=lambda x: x["time"],
            )
            return {
                "total": n,
                "by_severity": dict(by_sev),
                "by_attack_type": dict(by_atk),
                "avg_classify_ms": round(total_classify / n, 1),
                "avg_enrich_ms": round(total_enrich / n, 1),
                "avg_reason_ms": round(total_reason / n, 1),
                "avg_total_ms": round((total_classify + total_enrich + total_reason) / n, 1),
                "ioc_checked_pct": round(ioc_count / n * 100, 1),
                "reasoned_pct": round(reason_count / n * 100, 1),
                "unique_src_ips": len(src_ips),
                "unique_dst_ips": len(dst_ips),
                "timeline": timeline[-30:],
                "top_offending_ips": self.top_offending_ips(5),
                "alert_velocity": self.alert_velocity(5),
                "pipeline_success_rate": self.success_rate(),
            }
        finally:
            db.close()

    def correlate(self, min_alerts: int = 2) -> list[dict]:
        db = self._get_db()
        try:
            alerts = db.query(Alert).all()
            by_src = defaultdict(list)
            for a in alerts:
                src = a.src_ip
                if src:
                    by_src[src].append(a)

            clusters = []
            for src_ip, group in sorted(by_src.items(), key=lambda x: -len(x[1])):
                if len(group) < min_alerts:
                    continue
                severities = [a.severity or "low" for a in group]
                attack_types = list(set(a.attack_type or "" for a in group))
                clusters.append({
                    "src_ip": src_ip,
                    "alert_count": len(group),
                    "max_severity": "high" if "high" in severities else ("medium" if "medium" in severities else "low"),
                    "attack_types": attack_types,
                    "alert_ids": [a.id for a in group[:20]],
                    "first_seen": group[-1].timestamp.isoformat() if group[-1].timestamp else None,
                    "last_seen": group[0].timestamp.isoformat() if group[0].timestamp else None,
                })
            return clusters
        finally:
            db.close()


store = AlertStore()
