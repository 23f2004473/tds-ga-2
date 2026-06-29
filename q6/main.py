import time
from collections import deque

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

EMAIL   = "23f2004473@ds.study.iitm.ac.in"
START   = time.time()
COUNTER = Counter("http_requests_total", "Total HTTP requests to any endpoint")
LOGS    = deque(maxlen=1000)


@app.middleware("http")
async def observe(request: Request, call_next):
    COUNTER.inc()
    response = await call_next(request)
    LOGS.append({
        "level":  "info",
        "ts":     time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": response.status_code,
        "path":   request.url.path,
    })
    return response


@app.get("/work")
async def work(n: int = 1):
    return {"email": EMAIL, "done": n}


@app.get("/metrics")
async def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/healthz")
async def healthz():
    return {"status": "ok", "uptime_s": round(time.time() - START, 4)}


@app.get("/logs")
async def logs(n: int = 10):
    return list(LOGS)[-n:]
