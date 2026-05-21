import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import check_db_connection
from app.logging_config import setup_logging
from app.middleware import RequestIDMiddleware
from app.rate_limiter import limiter
from app.routers import auth, lectures, assignments, webhooks, dashboard

setup_logging()
logger = logging.getLogger(__name__)

_redis_client = None


def _get_redis():
    global _redis_client
    if _redis_client is None:
        import redis.asyncio as aioredis
        _redis_client = aioredis.from_url(settings.REDIS_URL)
    return _redis_client


async def _close_redis():
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application")
    await check_db_connection()
    logger.info("Database connection verified")
    yield
    await _close_redis()
    logger.info("Shutting down application")


app = FastAPI(
    title="Python Engineering Course Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(RequestIDMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(lectures.router)
app.include_router(assignments.router)
app.include_router(webhooks.router)
app.include_router(dashboard.router)


@app.get("/api/health")
async def health():
    checks = {"database": "ok", "redis": "ok"}
    try:
        await check_db_connection()
    except Exception:
        checks["database"] = "error"

    try:
        r = _get_redis()
        await r.ping()
    except Exception:
        checks["redis"] = "error"

    status = "ok" if all(v == "ok" for v in checks.values()) else "degraded"
    return {"status": status, "version": "1.0.0", "checks": checks}
