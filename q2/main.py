from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import jwt  # PyJWT[crypto]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- YOUR ASSIGNED VALUES ---
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuY
cxiP/hG8C6Sb91wg3yiLAA4HCnpITcbWCSe1bvbYGuc3EbNy4xFyf5CbjSDHJMID
EkryOgyd2giIIIBOUBjBS63uGcnRpOBh9NFatfNwheKuzsPuVNIdu6A9cNteNpXc
WyJJG2axVFmq7i6SuKr1JoWYG7xTTAvKPujS14OtsQf03h5NepzdfXpr28oNnzfW
ed+zclR68cmNNo/WVfJ4xyCL5f0BCOgdTgW6PdaChdil9VDetJZVEgC5tkyvXsfI
SI6iyrYbKR0NEB5qq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIX
dQIDAQAB
-----END PUBLIC KEY-----"""

ISSUER   = "https://idp.exam.local"
AUDIENCE = "tds-jpyssy71.apps.exam.local"
# ----------------------------


class TokenIn(BaseModel):
    token: str


@app.post("/verify")
async def verify(req: TokenIn):
    try:
        payload = jwt.decode(
            req.token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            issuer=ISSUER,
            audience=AUDIENCE,
        )
        return JSONResponse({
            "valid": True,
            "email": payload.get("email", ""),
            "sub":   payload.get("sub", ""),
            "aud":   payload.get("aud", ""),
        })
    except Exception:
        return JSONResponse({"valid": False}, status_code=401)
