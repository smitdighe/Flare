"""
Rate limiting middleware and input sanitization.
"""
import time
import re
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = 60

        self.requests[client_ip] = [t for t in self.requests[client_ip] if now - t < window]
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        self.requests[client_ip].append(now)

        response = await call_next(request)
        return response


def sanitize_input(value: str, max_length: int = 1000) -> str:
    if not isinstance(value, str):
        return value
    value = value[:max_length]
    value = re.sub(r'[<>"\']', '', value)
    return value


def sanitize_alert_data(alert: dict) -> dict:
    sanitized = {}
    for key, value in alert.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_input(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_alert_data(value)
        else:
            sanitized[key] = value
    return sanitized
