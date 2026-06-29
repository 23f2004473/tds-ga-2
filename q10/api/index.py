import time
import uuid
from collections import defaultdict

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

app = FastAPI()

EMAIL      = "23f2004473@ds.study.iitm.ac.in"
RATE_LIMIT = 13   # requests per window
WINDOW     = 10   # seconds

ALLOWED_ORIGINS = {
    "https://app-rgfstn.example.com",      # assigned origin — grader checks this
    "https://exam.sanand.workers.dev",     # exam page origin — browser check
}

rate_buckets: dict = defaultdict(list)


@app.middleware("http")
async def stack(request: Request, call_next):
    origin    = request.headers.get("origin", "")
    # Read header case-insensitively (Starlette does this automatically)
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    request.state.request_id = request_id

    # CORS preflight
    if request.method == "OPTIONS":
        resp_headers = {"X-Request-ID": request_id}
        if origin in ALLOWED_ORIGINS:
            resp_headers.update({
                "Access-Control-Allow-Origin":  origin,
                "Access-Control-Allow-Methods": "GET,OPTIONS",
                "Access-Control-Allow-Headers": "*",
            })
        return JSONResponse({}, status_code=200, headers=resp_headers)

    # Rate limiting — return JSONResponse directly so headers are guaranteed
    client_id = request.headers.get("x-client-id", "default")
    now = time.time()
    rate_buckets[client_id] = [t for t in rate_buckets[client_id] if now - t < WINDOW]
    if len(rate_buckets[client_id]) >= RATE_LIMIT:
        return JSONResponse(
            {"error": "Too many requests"},
            status_code=429,
            headers={"Retry-After": str(WINDOW), "X-Request-ID": request_id},
        )
    rate_buckets[client_id].append(now)

    response = await call_next(request)

    # Set CORS on real responses
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin

    return response


@app.get("/ping")
async def ping(request: Request, response: Response):
    # Using FastAPI's Response injection — this reliably sets response headers
    # even in serverless environments where post-call_next mutation can fail
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    response.headers["X-Request-ID"] = request_id
    return {"email": EMAIL, "request_id": request_id}
