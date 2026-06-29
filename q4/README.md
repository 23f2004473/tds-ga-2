# Q4 — Run locally, expose via tunnel

```bash
# 1. Build and start
docker compose up -d --build

# 2. Expose via cloudflared (install from https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)
cloudflared tunnel --url http://localhost:8000

# 3. Copy the https://xxxx.trycloudflare.com URL and paste it as your answer
```
