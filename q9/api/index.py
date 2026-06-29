import time
import uuid
from collections import defaultdict

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

EMAIL      = "23f2004473@ds.study.iitm.ac.in"
TOTAL      = 59   # T — your assigned total orders
RATE_LIMIT = 17   # R — requests allowed per window
WINDOW     = 10   # seconds

# Pre-generate order catalog IDs 1..T
ORDERS = [{"id": i, "item": f"item-{i}", "email": EMAIL} for i in range(1, TOTAL + 1)]

# In-memory stores (ephemeral — fine for exam)
idempotency_store: dict[str, dict] = {}
rate_buckets: dict[str, list]      = defaultdict(list)


def enforce_rate(client_id: str):
    now = time.time()
    rate_buckets[client_id] = [t for t in rate_buckets[client_id] if now - t < WINDOW]
    if len(rate_buckets[client_id]) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(WINDOW)},
        )
    rate_buckets[client_id].append(now)


@app.post("/orders", status_code=201)
async def create_order(
    request: Request,
    idempotency_key: str = Header(None, alias="Idempotency-Key"),
    x_client_id: str     = Header("anonymous"),
):
    enforce_rate(x_client_id)

    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header required")

    # Return cached response for duplicate keys
    if idempotency_key in idempotency_store:
        return JSONResponse(idempotency_store[idempotency_key], status_code=201)

    # Create new order
    try:
        body = await request.json()
    except Exception:
        body = {}

    order = {"id": str(uuid.uuid4()), "email": EMAIL, **body}
    idempotency_store[idempotency_key] = order
    return JSONResponse(order, status_code=201)


@app.get("/orders")
async def list_orders(
    cursor: str      = "0",
    limit: int       = 5,
    x_client_id: str = Header("anonymous"),
):
    enforce_rate(x_client_id)

    try:
        start = int(cursor)
    except (ValueError, TypeError):
        start = 0

    start = max(0, min(start, TOTAL))
    end   = min(start + limit, TOTAL)
    page  = ORDERS[start:end]

    # None signals end-of-catalog to the grader
    next_cursor = str(end) if end < TOTAL else None

    return {
        "items":       page,
        "next_cursor": next_cursor,
    }
