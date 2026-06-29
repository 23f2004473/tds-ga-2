import time
import uuid
from collections import defaultdict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# --- YOUR ASSIGNED VALUES ---
EMAIL          = "23f2004473@ds.study.iitm.ac.in"
ALLOWED_ORIGIN = "https://app-rgfstn.example.com"
RATE_LIMIT     = 13   # requests per window
WINDOW         = 10   # seconds
# ----------------------------

rate_buckets: dict = defaultdict(list)


@app.middleware("http")
async def stack(request: Request, call_next):
    origin = request.headers.get("origin", "")

    # MW1: Request context — propagate or generate request_id
    request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    request.state.request_id = request_id

    # MW2: CORS preflight handling
    if request.method == "OPTIONS":
        headers = {"X-Request-Id": request_id}
        if origin == ALLOWED_ORIGIN:
            headers.update({
                "Access-Control-Allow-Origin":  ALLOWED_ORIGIN,
                "Access-Control-Allow-Methods": "GET,OPTIONS",
                "Access-Control-Allow-Headers": "*",
            })
        return JSONResponse({}, status_code=200, headers=headers)

    # MW3: Per-client rate limiting
    client_id = request.headers.get("X-Client-Id", "default")
    now = time.time()
    rate_buckets[client_id] = [t for t in rate_buckets[client_id] if now - t < WINDOW]
    if len(rate_buckets[client_id]) >= RATE_LIMIT:
        return JSONResponse(
            {"error": "Too many requests"},
            status_code=429,
            headers={"Retry-After": str(WINDOW), "X-Request-Id": request_id},
        )
    rate_buckets[client_id].append(now)

    response = await call_next(request)

    # Always return request_id in response header
    response.headers["X-Request-Id"] = request_id

    # Attach ACAO header only for the allowed origin
    if origin == ALLOWED_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN

    return response


@app.get("/ping")
async def ping(request: Request):
    return {
        "email":      EMAIL,
        "request_id": request.state.request_id,
    }
