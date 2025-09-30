from __future__ import annotations
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from .config import settings


class ApiKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # If API key not set, allow all (dev mode)
        if not settings.api_key:
            return await call_next(request)

        key = request.headers.get("x-api-key")
        if not key:
            auth = request.headers.get("authorization", "")
            if auth.lower().startswith("bearer "):
                key = auth[7:]

        if key != settings.api_key:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)

        return await call_next(request)
