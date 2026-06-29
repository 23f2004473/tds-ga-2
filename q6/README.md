# Q6 — Production Observability

Prometheus counter MUST be live (not a static file) — deploy as a long-running process.

## Option A: Run locally + cloudflared tunnel
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
cloudflared tunnel --url http://localhost:8000
```

## Option B: Deploy to Render (free)
- Push to GitHub
- New Web Service on render.com → Python → Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Option C: Fly.io
```bash
fly launch
fly deploy
```

Submit your base URL (e.g. https://my-observability.onrender.com)
