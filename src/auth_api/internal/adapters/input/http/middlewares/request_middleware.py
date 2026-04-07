import time
import uuid

from fastapi import Request
from opentelemetry import trace
from starlette.middleware.base import BaseHTTPMiddleware

from auth_api.internal.ports.output.logger import Logger

REQUEST_ID_HEADER = "X-Request-ID"


def _get_trace_id(request_id: str) -> str | None:
    span = trace.get_current_span()
    if span.is_recording():
        span.set_attribute("request.id", request_id)

    span_context = span.get_span_context()
    if not span_context.is_valid:
        return None

    trace_id = f"{span_context.trace_id:032x}"
    return trace_id


class RequestContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        logger: Logger = request.app.state.logger.branch(
            component="request_context_middleware")
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        start_time = time.perf_counter()

        logger.clear_context()
        logger.bind_context(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
        )
        request.state.request_id = request_id

        trace_id = _get_trace_id(request_id)
        if trace_id:
            logger.bind_context(trace_id=trace_id)
            request.state.trace_id = trace_id

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "request_completed",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )
            response.headers[REQUEST_ID_HEADER] = request_id
            return response
        except Exception:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.exception(
                "request_failed",
                duration_ms=round(duration_ms, 2),
            )
            raise
        finally:
            logger.clear_context()
