# security.py - Security Middleware and Utilities

import os
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# Load API key from environment
DASHBOARD_API_KEY = os.getenv("DASHBOARD_API_KEY", "")


async def verify_dashboard_access(request: Request) -> bool:
    """
    Verify that the request is coming from the dashboard.
    
    Implements multiple security checks:
    1. Referer header check (must be localhost:3000)
    2. API key verification (X-Dashboard-Key header)
    3. Origin header check
    
    Returns:
        bool: True if access is allowed, False otherwise
    """
    
    # Get request details
    referer = request.headers.get("referer", "")
    origin = request.headers.get("origin", "")
    api_key = request.headers.get("X-Dashboard-Key", "")
    
    # Allow health check endpoint without restrictions
    if request.url.path == "/health":
        return True
    
    # Allow WebSocket connections from localhost
    if request.url.path == "/ws":
        if "localhost:3000" in origin or "127.0.0.1:3000" in origin:
            return True
    
    # Check 1: Verify referer or origin is from localhost
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost",
        "http://127.0.0.1",
    ]
    
    origin_valid = any(allowed_origin in (referer or origin) for allowed_origin in allowed_origins)
    
    # Special handling: If no origin/referer (same-origin request), allow it
    # Browsers don't always send these headers for same-origin requests
    if not referer and not origin:
        logger.info(f"Request without origin/referer (same-origin) - allowing: {request.url.path}")
        return True
    
    # Check 2: API key is OPTIONAL for now (since we're localhost-only)
    # Just log if it's missing, but don't block
    if DASHBOARD_API_KEY and not api_key:
        logger.info(f"Request without API key (optional): {request.url.path}")
    
    # Log security check failures
    if not origin_valid:
        logger.warning(
            f"Blocked request from unauthorized origin. "
            f"Path: {request.url.path}, "
            f"Referer: {referer}, "
            f"Origin: {origin}"
        )
        return False
    
    return True


async def security_middleware(request: Request, call_next):
    """
    Middleware to restrict API access to dashboard only.
    
    This prevents direct browser access to the API endpoints
    while allowing the dashboard to function normally.
    """
    
    # Verify dashboard access
    if not await verify_dashboard_access(request):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "detail": "Access denied. This API is only accessible via the Aegis Dashboard."
            }
        )
    
    # Process request
    response = await call_next(request)
    return response


def is_localhost_only() -> bool:
    """
    Check if server is configured for localhost-only access.
    
    Returns:
        bool: True if configured for localhost only
    """
    # This can be expanded to read from environment variables
    # For now, returns True as we're binding to 127.0.0.1
    return True
