import time
import uuid
from collections import defaultdict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

EMAIL = "23f2004473@ds.study.iitm.ac.in"

RATE_LIMIT = 13
WINDOW = 10

ALLOWED_ORIGINS = {
    "https://app-rgfstn.example.com",
    "https://exam.sanand.workers.dev",
}

rate_buckets = defaultdict(list)


@app.middleware("http")
async def middleware_stack(request: Request, call_next):
    origin = request.headers.get("origin")

    # -----------------------------
    # Request Context Middleware
    # -----------------------------
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = str(uuid.uuid4())

    request.state.request_id = request_id

    # -----------------------------
    # CORS Preflight
    # -----------------------------
    if request.method == "OPTIONS":
        headers = {
            "X-Request-ID": request_id,
        }

        if origin in ALLOWED_ORIGINS:
            headers.update({
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "X-Request-ID, X-Client-Id, Content-Type",
                "Access-Control-Expose-Headers": "X-Request-ID",
            })

        return JSONResponse({}, status_code=200, headers=headers)

    # -----------------------------
    # Rate Limiting
    # -----------------------------
    client = request.headers.get("X-Client-Id", "default")

    now = time.time()

    rate_buckets[client] = [
        t for t in rate_buckets[client]
        if now - t < WINDOW
    ]

    if len(rate_buckets[client]) >= RATE_LIMIT:
        headers = {
            "X-Request-ID": request_id,
            "Retry-After": str(WINDOW),
        }

        if origin in ALLOWED_ORIGINS:
            headers["Access-Control-Allow-Origin"] = origin
            headers["Access-Control-Expose-Headers"] = "X-Request-ID"

        return JSONResponse(
            {"detail": "Rate limit exceeded"},
            status_code=429,
            headers=headers,
        )

    rate_buckets[client].append(now)

    # -----------------------------
    # Continue request
    # -----------------------------
    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Expose-Headers"] = "X-Request-ID"

    return response


@app.get("/ping")
async def ping(request: Request):
    return {
        "email": EMAIL,
        "request_id": request.state.request_id,
    }