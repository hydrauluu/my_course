import logging
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

MAX_BODY_SIZE = 10 * 1024 * 1024  # 10MB


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method in ("POST", "PUT", "PATCH"):
            cl = request.headers.get("Content-Length")
            if cl and int(cl) > MAX_BODY_SIZE:
                return JSONResponse(status_code=413, content={"detail": "Request too large"})
        return await call_next(request)


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        request.state.request_id = request_id

        adapter = logging.LoggerAdapter(logger, {"request_id": request_id})
        adapter.info("Request started", extra={"method": request.method, "path": request.url.path})

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        adapter.info("Request completed", extra={"status_code": response.status_code})
        return response
