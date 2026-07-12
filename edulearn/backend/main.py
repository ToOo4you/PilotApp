"""
EduLearn AI — FastAPI application entry point
"""
import json
import logging
import os
import time
import uuid
from collections import defaultdict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("edulearn.api")

app = FastAPI(
    title="EduLearn AI",
    description="AI-powered educational platform for autism, ADHD, and learning differences",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

def _cors_origins() -> list:
    defaults = [
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ]
    raw = os.getenv("CORS_ORIGINS", "")
    if not raw:
        return defaults
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [str(o) for o in parsed if str(o).strip()]
    except Exception:
        pass
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    return parts or defaults


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Observability middleware
# ---------------------------------------------------------------------------

app.state.metrics = {
    "requests_total": 0,
    "status_counts": defaultdict(int),
    "last_request_at": None,
}


@app.middleware("http")
async def observability(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000

    app.state.metrics["requests_total"] += 1
    app.state.metrics["status_counts"][str(response.status_code)] += 1
    app.state.metrics["last_request_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"

    logger.info(
        "request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
        request_id, request.method, request.url.path, response.status_code, duration_ms,
    )
    return response

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

from edulearn.backend.routes.education import router as education_router

app.include_router(education_router)

# ---------------------------------------------------------------------------
# Root & metrics
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {
        "service": "EduLearn AI",
        "description": "AI-powered education platform for diverse learners",
        "docs": "/docs",
        "health": "/api/education/health",
    }


@app.get("/metrics")
def metrics():
    return JSONResponse({
        "requests_total": app.state.metrics["requests_total"],
        "status_counts": dict(app.state.metrics["status_counts"]),
        "last_request_at": app.state.metrics["last_request_at"],
    })
