import time
import uuid
from collections import defaultdict

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

app = FastAPI()

EMAIL      = "23f2004473@ds.study.iitm.ac.in"
RATE_LIMIT = 13
WINDOW     = 10  # seconds

ALLOWED_ORIGINS = {
    "https://app-rgfstn.example.com",
    "https://exam.sanand.workers.dev",
}

rate_buckets: dict = defaultdict(list)

# Headers the browser is allowed to read (must be exposed via CORS)
EXPOSE = "X-Request-ID"


@app.middleware("http")
async def stack(request: Request, call_next):
    origin     = request.headers.get("origin", "")
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    request.state.request_id = request_id

    # --- CORS preflight ---
    if request.method == "OPTIONS":
        resp_headers = {
            "X-Request-ID":                    request_id,
            "Cache-Control":                   "no-store",
        }
        if origin in ALLOWED_ORIGINS:
            resp_headers.update({
                "Access-Control-Allow-Origin":   origin,
                "Access-Control-Allow-Methods":  "GET,OPTIONS",
                "Access-Control-Allow-Headers":  "*",
                "Access-Control-Expose-Headers": EXPOSE,
            })
        return JSONResponse({}, status_code=200, headers=resp_headers)

    # --- Rate limiting ---
    client_id = request.headers.get("x-client-id", "default")
    now = time.time()
    rate_buckets[client_id] = [t for t in rate_buckets[client_id] if now - t < WINDOW]
    if len(rate_buckets[client_id]) >= RATE_LIMIT:
        return JSONResponse(
            {"error": "Too many requests"},
            status_code=429,
            headers={
                "Retry-After":   str(WINDOW),
                "X-Request-ID":  request_id,
                "Cache-Control": "no-store",
            },
        )
    rate_buckets[client_id].append(now)

    return await call_next(request)


@app.get("/ping")
async def ping(request: Request, response: Response):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    origin     = request.headers.get("origin", "")

    # Set all headers directly on the response — most reliable in serverless
    response.headers["X-Request-ID"]  = request_id
    response.headers["Cache-Control"] = "no-store"

    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"]   = origin
        # Expose-Headers tells the browser it is ALLOWED to read X-Request-ID
        response.headers["Access-Control-Expose-Headers"] = EXPOSE

    return {"email": EMAIL, "request_id": request_id}
