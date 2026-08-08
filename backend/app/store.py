"""
Thread-safe in-memory alert store. Every triaged alert is appended here so
that /alerts, /stats, /alerts/correlated, and /eval can query against the
actual alerts the pipeline has processed — not just what's on screen.
"""
import threading
import time
from collections import defaultdict
from typing import Optional


class AlertStore:
    def __init__(self, max_size: int = 500):
        self._lock = threading.Lock()
        self._alerts: list[dict] = []
        self._max_size = max_size

    def append(self, alert: dict):
        with self._lock:
            self._alerts.insert(0, alert)
            if len(self._alerts) > self._max_size:
                self._alerts = self._alerts[:self._max_size]

    def all(self) -> list[dict]:
        with self._lock:
            return list(self._alerts)

    def count(self) -> int:
        with self._lock:
            return len(self._alerts)

    def get_by_id(self, alert_id: str) -> Optional[dict]:
        with self._lock:
            for a in self._alerts:
                if a.get("id") == alert_id:
                    return dict(a)
        return None

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
        with self._lock:
            results = list(self._alerts)

        if severity:
            results = [a for a in results if a.get("severity") == severity]
        if attack_type:
            results = [a for a in results if a.get("attack_type") == attack_type]
        if min_severity:
            min_val = sev_order.get(min_severity, 0)
            results = [a for a in results if sev_order.get(a.get("severity"), 0) >= min_val]
        if search:
            q = search.lower()
            results = [
                a for a in results
                if q in (a.get("signature", "")).lower()
                or q in (a.get("src_ip", "")).lower()
                or q in (a.get("dest_ip", "")).lower()
                or q in (a.get("id", "")).lower()
            ]

        total = len(results)
        return {"alerts": results[offset:offset + limit], "total": total, "offset": offset, "limit": limit}

    def top_offending_ips(self, limit: int = 10) -> list[dict]:
        with self._lock:
            alerts = list(self._alerts)

        by_src = defaultdict(lambda: {"count": 0, "severities": [], "types": set()})
        for a in alerts:
            src = a.get("src_ip", "")
            if src:
                by_src[src]["count"] += 1
                by_src[src]["severities"].append(a.get("severity", "low"))
                by_src[src]["types"].add(a.get("attack_type", "unknown"))

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

    def alert_velocity(self, minutes: int = 5) -> float:
        cutoff = time.time() - (minutes * 60)
        with self._lock:
            count = 0
            for a in self._alerts:
                ts = a.get("timestamp", "")
                if ts:
                    try:
                        alert_time = time.mktime(time.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S"))
                        if alert_time >= cutoff:
                            count += 1
                    except (ValueError, OverflowError):
                        pass
        return round(count / max(minutes, 1), 2)

    def success_rate(self) -> float:
        with self._lock:
            alerts = list(self._alerts)

        if not alerts:
            return 0.0

        completed = sum(
            1 for a in alerts
            if a.get("severity") and a.get("classify_latency_ms") is not None
        )
        return round(completed / len(alerts) * 100, 1)

    def stats(self) -> dict:
        with self._lock:
            alerts = list(self._alerts)

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
            sev = a.get("severity", "unknown")
            atk = a.get("attack_type", "unknown")
            by_sev[sev] += 1
            by_atk[atk] += 1
            total_classify += a.get("classify_latency_ms") or 0
            total_enrich += a.get("enrich_latency_ms") or 0
            total_reason += a.get("reasoning_latency_ms") or 0
            if a.get("ioc_checked"):
                ioc_count += 1
            if a.get("explanation"):
                reason_count += 1
            src_ips.add(a.get("src_ip", ""))
            dst_ips.add(a.get("dest_ip", ""))

            ts = a.get("timestamp", "")
            if ts:
                bucket = ts[:16]
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

    def correlate(self, min_alerts: int = 2) -> list[dict]:
        with self._lock:
            alerts = list(self._alerts)

        by_src = defaultdict(list)
        for a in alerts:
            src = a.get("src_ip", "")
            if src:
                by_src[src].append(a)

        clusters = []
        for src_ip, group in sorted(by_src.items(), key=lambda x: -len(x[1])):
            if len(group) < min_alerts:
                continue
            severities = [a.get("severity", "low") for a in group]
            attack_types = list(set(a.get("attack_type", "") for a in group))
            clusters.append({
                "src_ip": src_ip,
                "alert_count": len(group),
                "max_severity": "high" if "high" in severities else ("medium" if "medium" in severities else "low"),
                "attack_types": attack_types,
                "alert_ids": [a.get("id") for a in group[:20]],
                "first_seen": group[-1].get("timestamp"),
                "last_seen": group[0].get("timestamp"),
            })

        return clusters


store = AlertStore()
