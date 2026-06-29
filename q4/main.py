import os
import redis as r
from fastapi import FastAPI

app = FastAPI()
rd = r.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379"),
    decode_responses=True,
)


@app.post("/hit/{key}")
async def hit(key: str):
    count = rd.incr(key)
    return {"key": key, "count": count}


@app.get("/count/{key}")
async def count(key: str):
    val = rd.get(key)
    return {"key": key, "count": int(val) if val else 0}


@app.get("/healthz")
async def healthz():
    try:
        rd.ping()
        redis_status = "up"
    except Exception:
        redis_status = "down"
    return {"status": "ok", "redis": redis_status}
