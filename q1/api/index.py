import uuid, time, statistics
from fastapi import FastAPI, Request
from fastapi.responses import Response, JSONResponse

app = FastAPI()
ALLOWED_ORIGIN = "https://dash-5c0zqy.example.com"
EMAIL = "23f2004473@ds.study.iitm.ac.in"

@app.middleware("http")
async def middleware(request: Request, call_next):
    origin = request.headers.get("origin", "")
    req_id = str(uuid.uuid4())
    start = time.perf_counter()

    # Handle CORS preflight
    if request.method == "OPTIONS":
        if origin == ALLOWED_ORIGIN:
            return Response(status_code=200, headers={
                "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
                "Access-Control-Allow-Methods": "GET,OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "X-Request-Id": req_id,
                "X-Process-Time": "0",
            })
        return Response(status_code=200, headers={
            "X-Request-Id": req_id, "X-Process-Time": "0"
        })

    response = await call_next(request)
    elapsed = time.perf_counter() - start
    response.headers["X-Request-Id"] = req_id
    response.headers["X-Process-Time"] = str(elapsed)
    if origin == ALLOWED_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
    return response

@app.get("/stats")
async def stats(values: str):
    nums = [int(v) for v in values.split(",")]
    return {
        "email": EMAIL,
        "count": len(nums),
        "sum": sum(nums),
        "min": min(nums),
        "max": max(nums),
        "mean": statistics.mean(nums),
    }