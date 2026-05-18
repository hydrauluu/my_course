import logging
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


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
