import logging
import os
import time
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from prometheus_client import Counter, Histogram

from app.database import close_db, init_db
from app.routes.api import router as api_router
from app.routes.booking import router as booking_router
from app.routes.pages import router as pages_router

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("backend")

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path", "status"],
)
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)


@asynccontextmanager
async def lifespan(app):
    await init_db()
    yield
    await close_db()


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def track_metrics(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start

    method = request.method
    path = request.url.path
    status = str(response.status_code)

    REQUEST_DURATION.labels(method=method, path=path, status=status).observe(duration)
    REQUEST_COUNT.labels(method=method, path=path, status=status).inc()

    logger.info(
        "request completed method=%s path=%s status=%s duration_ms=%.2f",
        method,
        path,
        status,
        duration * 1000,
    )
    return response


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


app.include_router(api_router)
app.include_router(booking_router)
app.include_router(pages_router)

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
