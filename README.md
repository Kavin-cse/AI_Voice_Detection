# AI-Generated Voice Detection (Multi-Language)

## Overview
A FastAPI-based REST service to classify an input MP3 voice sample as `AI_GENERATED` or `HUMAN`.

## Quickstart (local)
1. Copy `.env.example` to `.env` and set `API_KEY`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Train a model (optional): `python scripts/train.py` (this generates a model at `app/artifacts/model.joblib`). If you skip training the server will train a fallback lightweight model at startup.
4. Run server: `uvicorn app.main:app --host 0.0.0.0 --port 8000` or `./start.sh`.
5. Expose via ngrok or deploy to cloud for a public HTTPS endpoint.

---

## Deployment & HTTPS (recommended quick method)
- Use ngrok for a temporary public HTTPS endpoint:
  1. Start the app: `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
  2. In another terminal run: `ngrok http 8000`.
  3. Use the generated `https://` URL to send requests.

- Docker:
  1. Build: `docker build -t ai-voice-detector .`
  2. Run: `docker run -e API_KEY=your_key -p 8000:8000 ai-voice-detector`

> Note: Make sure `ffmpeg` is available in your runtime (the Dockerfile already installs it).
## API
POST `/api/voice-detection` with headers `Content-Type: application/json` and `x-api-key: <API_KEY>`.

Request JSON (strict):
```
{
  "language": "Tamil | English | Hindi | Malayalam | Telugu",
  "audioFormat": "mp3",
  "audioBase64": "<Base64 encoded MP3 audio>"
}
```

Successful response:
```
{
  "status": "success",
  "language": "<same as input>",
  "classification": "AI_GENERATED | HUMAN",
  "confidenceScore": 0.0,
  "explanation": "<short reason>"
}
```

Error response:
```
{
  "status": "error",
  "message": "<error description>"
}
```

### Example (curl)

curl -X POST https://<PUBLIC_URL>/api/voice-detection \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{"language":"English","audioFormat":"mp3","audioBase64":"<...>"}'

