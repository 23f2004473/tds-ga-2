import os
import yaml
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Layer 1: hardcoded defaults
DEFAULTS = {
    "port":      8000,
    "workers":   1,
    "debug":     False,
    "log_level": "info",
    "api_key":   "default-secret-000",
}


def coerce(key: str, val):
    if key in ("port", "workers"):
        return int(val)
    if key == "debug":
        return str(val).lower() in ("true", "1", "yes", "on")
    return str(val)


@app.get("/effective-config")
async def effective_config(request: Request):
    cfg = dict(DEFAULTS)

    # Layer 2: config.development.yaml
    try:
        with open("config.development.yaml") as f:
            for k, v in (yaml.safe_load(f) or {}).items():
                if k in cfg:
                    cfg[k] = coerce(k, v)
    except FileNotFoundError:
        pass

    # Layer 3: .env file (supports NUM_WORKERS alias)
    try:
        with open(".env") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    k = k.strip()
                    if k == "NUM_WORKERS":
                        k = "workers"
                    if k in cfg:
                        cfg[k] = coerce(k, v.strip())
    except FileNotFoundError:
        pass

    # Layer 4: OS env vars with APP_* prefix
    for env_k, env_v in os.environ.items():
        if env_k.startswith("APP_"):
            k = env_k[4:].lower()
            if k == "num_workers":
                k = "workers"
            if k in cfg:
                cfg[k] = coerce(k, env_v)

    # Layer 5: ?set-key=value query params (highest priority)
    for param, val in request.query_params.items():
        if param.startswith("set-"):
            k = param[4:]
            if k in cfg:
                cfg[k] = coerce(k, val)

    # Always mask api_key
    cfg["api_key"] = "*****"
    return cfg
