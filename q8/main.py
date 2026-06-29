import json
import re

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Change these if you use a different model or port
OLLAMA_URL = "http://localhost:11434/v1/chat/completions"
MODEL      = "llama3.2"

SYSTEM_PROMPT = (
    "You are an invoice parser. "
    "Extract fields from the invoice text and return ONLY a valid JSON object with exactly these keys: "
    'vendor (string), amount (number), currency (3-letter uppercase string like USD), date (YYYY-MM-DD string). '
    "No explanation. No markdown. JSON only."
)


class InvoiceReq(BaseModel):
    text: str


class InvoiceResp(BaseModel):
    vendor:   str
    amount:   float
    currency: str
    date:     str


@app.post("/extract", response_model=InvoiceResp)
async def extract(req: InvoiceReq):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=422, detail="Empty input")

    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": req.text},
                ],
                "temperature": 0,
            },
            timeout=60,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]

        # Extract JSON block from the response
        m = re.search(r"\{.*?\}", content, re.DOTALL)
        if not m:
            raise ValueError("No JSON in model response")

        data = json.loads(m.group())
        return InvoiceResp(
            vendor=str(data["vendor"]),
            amount=float(data["amount"]),
            currency=str(data["currency"]).upper()[:3],
            date=str(data["date"]),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
