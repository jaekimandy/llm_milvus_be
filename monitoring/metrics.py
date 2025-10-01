from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST
from fastapi import Response
import time


# Define metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

active_requests = Gauge(
    'active_requests',
    'Number of active requests'
)

ai_agent_requests_total = Counter(
    'ai_agent_requests_total',
    'Total AI agent requests',
    ['agent_type', 'status']
)

ai_agent_duration_seconds = Histogram(
    'ai_agent_duration_seconds',
    'AI agent processing duration in seconds',
    ['agent_type']
)

database_queries_total = Counter(
    'database_queries_total',
    'Total database queries',
    ['operation', 'table']
)

encryption_operations_total = Counter(
    'encryption_operations_total',
    'Total encryption operations',
    ['operation']
)


class MetricsMiddleware:
    """Middleware to collect HTTP metrics"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope["method"]
        path = scope["path"]

        active_requests.inc()
        start_time = time.time()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                duration = time.time() - start_time

                http_requests_total.labels(
                    method=method,
                    endpoint=path,
                    status=status_code
                ).inc()

                http_request_duration_seconds.labels(
                    method=method,
                    endpoint=path
                ).observe(duration)

                active_requests.dec()

            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            active_requests.dec()
            raise e


def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
