"""
Structured error handling and request ID middleware.
"""
import uuid
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("flare")


async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", None)
    logger.error(f"Unhandled exception: {exc}", exc_info=True, extra={"request_id": request_id, "path": request.url.path})
    return JSONResponse(
        status_code=500,
        content={"ok": False, "error": "Internal server error", "request_id": request_id},
    )


async def http_exception_handler(request: Request, exc):
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=exc.status_code,
        content={"ok": False, "error": exc.detail, "request_id": request_id},
    )


class RequestIDMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        request = Request(scope, receive)
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        scope["state"] = getattr(scope, "state", {})
        scope["state"]["request_id"] = request_id

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode()))
                message["headers"] = headers
            return await send(message)

        return await self.app(scope, receive, send_wrapper)
