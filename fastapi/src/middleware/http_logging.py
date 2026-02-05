import logging
import time
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from src.utils.logger import get_logger

logger = get_logger(__name__)


class HTTPLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования HTTP‑запросов."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """Логирование всех HTTP‑запросов в формате access‑log."""

        start_time = time.time()
        client_host = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        query_string = str(request.url.query)
        if query_string:
            path = f"{path}?{query_string}"
        protocol = request.scope.get("http_version", "HTTP/1.1")
        if not protocol.startswith("HTTP/"):
            protocol = f"HTTP/{protocol}"

        status_code = 500  # По умолчанию, если произойдет ошибка
        response: Response | None = None
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as exc:
            # Логируем запрос даже если произошла ошибка
            logger.error(f"Ошибка при обработке запроса {method} {path}", exc_info=True)
            raise exc
        finally:
            process_time = time.time() - start_time
            log_message = f'{client_host} - "{method} {path} {protocol}" {status_code} {process_time:.3f}s'
            # Логируем и через модульный логгер, и через root‑логгер,
            # чтобы гарантированно попасть и в app.log, и в stdout контейнера.
            logger.info(log_message)
            logging.getLogger().info(log_message)

        return response
