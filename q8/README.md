# Q8 — Local LLM Structured-Output Service

Requires Ollama running locally (same machine as this FastAPI app).

## Steps

### 1. Make sure Ollama + model is ready
```bash
ollama pull llama3.2
ollama serve          # port 11434
```

### 2. Run this FastAPI app
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001
```

### 3. Expose via cloudflared
```bash
cloudflared tunnel --url http://localhost:8001
# Get: https://xxxx.trycloudflare.com
```

### 4. Submit your /extract endpoint URL:
https://xxxx.trycloudflare.com/extract
