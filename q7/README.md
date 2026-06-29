# Q7 — Expose a Local LLM through a Tunnel

## Steps

### 1. Install Ollama
Download from https://ollama.ai and install.

### 2. Pull a model
```bash
ollama pull llama3.2
```

### 3. Make sure Ollama is running
```bash
ollama serve
# Runs on http://localhost:11434
```

### 4. Expose via cloudflared
```bash
cloudflared tunnel --url http://localhost:11434
# You'll get: https://xxxx.trycloudflare.com
```

### 5. Submit this JSON in the exam answer box:
```json
{"url": "https://xxxx.trycloudflare.com/v1/chat/completions", "model": "llama3.2"}
```

Replace `xxxx` with your actual tunnel subdomain.
Replace `llama3.2` with the exact model name you pulled (check with `ollama list`).
