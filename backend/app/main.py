import json
import logging
import os
import time
import uuid
from collections import defaultdict
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from backend.database.db import engine
from backend.database.models import Base, Company
from fastapi import APIRouter
from pydantic import BaseModel

try:
    import redis as redis_lib
except Exception:
    redis_lib = None


logger = logging.getLogger("pilot.api")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

FRONTEND_DIST_DIR = Path(__file__).resolve().parents[2] / "frontend" / "dist"
FRONTEND_ASSETS_DIR = FRONTEND_DIST_DIR / "assets"


def _load_allowed_origins():
    default_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:4174",
        "http://127.0.0.1:4174",
    ]
    raw = os.getenv("CORS_ORIGINS", "")
    if not raw:
        return default_origins

    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [str(origin) for origin in parsed if str(origin).strip()]
    except Exception:
        pass

    split_values = [part.strip() for part in raw.split(",") if part.strip()]
    return split_values or default_origins


def _load_rate_limit_overrides():
    # Safer defaults for sensitive auth routes.
    defaults = {
        "/auth/login": 20,
        "/auth/register": 15,
    }

    raw = os.getenv("RATE_LIMIT_PATH_OVERRIDES", "")
    if not raw:
        return defaults

    parsed_overrides = None
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            parsed_overrides = parsed
    except Exception:
        parsed_overrides = None

    if parsed_overrides is None:
        return defaults

    merged = dict(defaults)
    for key, value in parsed_overrides.items():
        try:
            merged[str(key)] = int(value)
        except Exception:
            continue

    return merged


def _resolve_path_limit(path: str, default_limit: int, overrides: dict) -> int:
    if path in overrides:
        return max(1, int(overrides[path]))

    # Prefix matcher with wildcard syntax, e.g. /auth/*
    matched_limit = None
    matched_prefix_len = -1
    for key, value in overrides.items():
        if not key.endswith("*"):
            continue
        prefix = key[:-1]
        if path.startswith(prefix) and len(prefix) > matched_prefix_len:
            matched_prefix_len = len(prefix)
            matched_limit = int(value)

    if matched_limit is not None:
        return max(1, matched_limit)

    return max(1, int(default_limit))

class JaxRequest(BaseModel):
    task: str
app = FastAPI()
app.state.metrics = {
    "requests_total": 0,
    "status_counts": defaultdict(int),
    "path_counts": defaultdict(int),
    "last_request_at": None,
}
app.state.rate_limit_store = {}
app.state.rate_limit_window_seconds = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
app.state.rate_limit_max_requests = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "120"))
app.state.rate_limit_backend = os.getenv("RATE_LIMIT_BACKEND", "auto").strip().lower()
setattr(app.state, "rate_limit_redis", None)
app.state.rate_limit_path_overrides = _load_rate_limit_overrides()


def _init_rate_limit_redis_client() -> Optional[object]:
    if redis_lib is None:
        logger.warning("Rate limiting: redis package not installed, using memory backend")
        return None

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    try:
        client = redis_lib.Redis.from_url(redis_url, decode_responses=True)
        client.ping()
        logger.info("Rate limiting: connected to redis backend")
        return client
    except Exception as exc:
        logger.warning("Rate limiting: redis unavailable (%s), using memory backend", exc)
        return None


if app.state.rate_limit_backend in {"auto", "redis"}:
    app.state.rate_limit_redis = _init_rate_limit_redis_client()


def _increment_memory_counter(key: str, now: float, window: int):
    item = app.state.rate_limit_store.get(key)
    if item is None or now >= item["reset_at"]:
        item = {"count": 0, "reset_at": now + window}

    item["count"] += 1
    app.state.rate_limit_store[key] = item
    return item["count"], int(item["reset_at"])


def _increment_redis_counter(key: str, now: float, window: int):
    client = app.state.rate_limit_redis
    if client is None:
        return None

    count = int(client.incr(key))
    ttl = int(client.ttl(key))
    if ttl < 0:
        client.expire(key, window)
        ttl = window
    return count, int(now + ttl)

@app.post("/jax/ask")
def ask_jax(request: JaxRequest):
    return {
        "message": f"JAX received your command: {request.task}. I am reviewing operations now."
    }


@app.middleware("http")
async def request_observability_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000

    app.state.metrics["requests_total"] += 1
    app.state.metrics["status_counts"][str(response.status_code)] += 1
    app.state.metrics["path_counts"][request.url.path] += 1
    app.state.metrics["last_request_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    logger.info(
        "request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )

    return response


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    path = request.url.path
    if path in {"/metrics", "/api/ai/health"}:
        return await call_next(request)

    client = request.client.host if request.client else "unknown"

    now = time.time()
    window = app.state.rate_limit_window_seconds
    max_requests = _resolve_path_limit(
        path,
        app.state.rate_limit_max_requests,
        app.state.rate_limit_path_overrides,
    )
    key = f"{client}:{path}"

    use_redis = app.state.rate_limit_backend in {"auto", "redis"} and app.state.rate_limit_redis is not None
    counter = None
    if use_redis:
        try:
            counter = _increment_redis_counter(f"rate:{key}", now, window)
        except Exception as exc:
            logger.warning("Rate limiting: redis increment failed (%s), using memory fallback", exc)

    if counter is None:
        count, reset_at = _increment_memory_counter(key, now, window)
    else:
        count, reset_at = counter

    if count > max_requests:
        retry_after = max(1, int(reset_at - now))
        app.state.metrics["status_counts"]["429"] += 1
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"},
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(max_requests),
                "X-RateLimit-Remaining": "0",
            },
        )

    response = await call_next(request)
    remaining = max(0, max_requests - count)
    response.headers["X-RateLimit-Limit"] = str(max_requests)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(reset_at))
    return response
trucks_router = APIRouter(
    prefix="/trucks",
    tags=["Trucks"]
)

trucks = [
    {
        "id": 1,
        "number": "T-101",
        "make": "Peterbilt",
        "model": "579",
        "year": 2023,
        "status": "Available"
    }
]

@trucks_router.get("/")
def get_trucks():
    return trucks


@app.on_event("startup")
def initialize_database_schema():
    auto_init = os.getenv("DB_AUTO_INIT")
    if auto_init is None:
        auto_init = "false" if os.getenv("APP_ENV", "development").lower() == "production" else "true"

    if auto_init.lower() != "true":
        logger.info("Skipping automatic database schema initialization (DB_AUTO_INIT=%s)", auto_init)
        return

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema initialization completed")
    except Exception as exc:
        logger.exception("Database schema initialization failed: %s", exc)


app.add_middleware(
    CORSMiddleware,
    allow_origins=_load_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers after app and middleware setup to reduce import-time side effects.
from backend.routes.companies import router as companies_router
from backend.routes.drivers import router as drivers_router
from backend.routes.auth import router as auth_router
from backend.routes.dashboard import router as dashboard_router
from backend.routes.jobs import router as jobs_router
from backend.routes.customers import router as customers_router
from backend.routes.ai_routes import router as ai_router
from backend.routes.operations import router as operations_router
from backend.routes.trailers import router as trailers_router

app.include_router(companies_router)
app.include_router(drivers_router)
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(jobs_router)
app.include_router(customers_router)
app.include_router(trucks_router)
app.include_router(trailers_router)
app.include_router(ai_router)
app.include_router(operations_router)

if FRONTEND_ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_ASSETS_DIR)), name="frontend-assets")

@app.get("/")
def home():
    index_file = FRONTEND_DIST_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)

    return {"message": "Pilot App API Running"}


@app.get("/metrics")
def metrics():
    status_counts = dict(app.state.metrics["status_counts"])
    path_counts = dict(app.state.metrics["path_counts"])
    return JSONResponse(
        {
            "requests_total": app.state.metrics["requests_total"],
            "status_counts": status_counts,
            "path_counts": path_counts,
            "last_request_at": app.state.metrics["last_request_at"],
        }
    )

    