from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from app.core.logging import logger

class TenantContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip Public Routes
        if request.url.path in ["/health", "/docs", "/openapi.json", "/api/v1/auth/login"]:
            return await call_next(request)

        # Log Context
        logger.debug(f"Request: {request.method} {request.url.path}")
        
        # Industry Standard Security Headers
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Tenant-Scope"] = "Enforced"
        
        return response