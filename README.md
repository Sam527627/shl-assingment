# SHL Assessment Recommender

Conversational agent that recommends SHL Individual Test Solutions via a FastAPI service.

## Files
```
main.py          ← FastAPI app (the agent)
catalog.json     ← SHL product catalog (Individual Test Solutions)
requirements.txt ← Python dependencies
Procfile         ← For Railway/Render deployment
runtime.txt      ← Python version
```

## Run locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your Anthropic API key
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Start the server
uvicorn main:app --host 0.0.0.0 --port 8000
```

Then open: http://localhost:8000/health  →  should return {"status":"ok"}

## API

### GET /health
Returns `{"status": "ok"}` with HTTP 200.

### POST /chat
```json
{
  "messages": [
    {"role": "user", "content": "I am hiring a Java developer"},
    {"role": "assistant", "content": "What seniority level?"},
    {"role": "user", "content": "Mid-level, 4 years experience"}
  ]
}
```

Response:
```json
{
  "reply": "Here are 4 assessments for a mid-level Java developer...",
  "recommendations": [
    {"name": "Java 8 (New)", "url": "https://www.shl.com/...", "test_type": "K"},
    {"name": "Verify Inductive Reasoning", "url": "https://www.shl.com/...", "test_type": "A"}
  ],
  "end_of_conversation": false
}
```

## Deploy to Railway (free, recommended)

1. Go to https://railway.app and sign up (free)
2. Click "New Project" → "Deploy from GitHub repo"
3. Push this folder to a GitHub repo first (see below)
4. Add environment variable: `ANTHROPIC_API_KEY` = your key
5. Railway auto-detects Procfile and deploys
6. Copy the public URL → submit that as your endpoint

### Push to GitHub
```bash
git init
git add .
git commit -m "SHL recommender"
gh repo create shl-recommender --public --push
```

## Deploy to Render (alternative free option)

1. Go to https://render.com and sign up
2. New → Web Service → Connect GitHub repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add env var: `ANTHROPIC_API_KEY`
