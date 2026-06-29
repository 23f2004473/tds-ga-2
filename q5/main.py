from collections import defaultdict
from typing import List

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- YOUR ASSIGNED VALUES ---
API_KEY = "ak_m2fqjgi4rykhbugoc2j4mh1e"
EMAIL   = "23f2004473@ds.study.iitm.ac.in"
# ----------------------------


class Event(BaseModel):
    user: str
    amount: float
    ts: int


class Batch(BaseModel):
    events: List[Event]


@app.post("/analytics")
async def analytics(batch: Batch, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    evs = batch.events
    user_totals: dict = defaultdict(float)
    for e in evs:
        if e.amount > 0:
            user_totals[e.user] += e.amount

    revenue  = sum(user_totals.values())
    top_user = max(user_totals, key=user_totals.get) if user_totals else ""

    return {
        "email":        EMAIL,
        "total_events": len(evs),
        "unique_users": len({e.user for e in evs}),
        "revenue":      revenue,
        "top_user":     top_user,
    }
