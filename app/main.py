import os
import base64
from fastapi import FastAPI, Request, Header, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from app.schemas import VoiceRequest, SuccessResponse, ErrorResponse
from app.auth import validate_api_key
from app.utils import b64_to_wav_np
from app.features import extract_features
from app.model import predict, explain
from starlette.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse
from pathlib import Path

load_dotenv()

app = FastAPI(title='AI Voice Detection')


@app.get('/health')
async def health():
    return {'status': 'ok'}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={'status': 'error', 'message': exc.detail})


@app.post('/api/voice-detection', response_model=SuccessResponse)
async def voice_detection(req: VoiceRequest, request: Request, x_api_key: str | None = Header(None)):
    # Validate API key
    try:
        validate_api_key(x_api_key)
    except HTTPException as e:
        raise e

    # Validate language and format already done by pydantic
    # Decode audio
    try:
        y, sr = b64_to_wav_np(req.audioBase64)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=400, detail='Unable to decode audio')

    # Extract features
    feature_vec, features = extract_features(y, sr)

    # Run model
    try:
        label, confidence, meta = predict(feature_vec)
    except Exception as e:
        raise HTTPException(status_code=500, detail='Model inference failed')

    explanation = explain(features, label)

    return JSONResponse(status_code=200, content={
        'status': 'success',
        'language': req.language,
        'classification': label,
        'confidenceScore': round(confidence, 4),
        'explanation': explanation
    })



@app.websocket('/ws/voice')
async def ws_voice(websocket: WebSocket):
    # WebSocket endpoint to receive base64-encoded audio chunks and return classification
    await websocket.accept()
    # Expect API key as query param: ws://.../ws/voice?x_api_key=KEY
    x_api_key = websocket.query_params.get('x_api_key')
    if x_api_key is None:
        await websocket.send_json({'status': 'error', 'message': 'Missing API key'})
        await websocket.close()
        return

    try:
        validate_api_key(x_api_key)
    except HTTPException as e:
        await websocket.send_json({'status': 'error', 'message': e.detail})
        await websocket.close()
        return

    chunks = []
    try:
        while True:
            msg = await websocket.receive_text()
            if msg == 'END':
                break
            if msg == 'CANCEL':
                chunks = []
                await websocket.send_text('CANCELLED')
                continue
            # Accept base64 chunk
            try:
                b = base64.b64decode(msg)
                chunks.append(b)
            except Exception:
                await websocket.send_json({'status': 'error', 'message': 'Invalid base64 chunk'})

        # Combine all received bytes
        mp3_bytes = b''.join(chunks)

        # Convert and load wav in threadpool to avoid blocking
        try:
            # re-use existing base64-driven helper (it will run ffmpeg if necessary)
            combined_b64 = base64.b64encode(mp3_bytes).decode('ascii')
            y, sr = await run_in_threadpool(b64_to_wav_np, combined_b64)
        except Exception as e:
            await websocket.send_json({'status': 'error', 'message': 'Unable to decode audio: ' + str(e)})
            await websocket.close()
            return

        # Feature extraction + model inference in threadpool
        try:
            feature_vec, features = await run_in_threadpool(extract_features, y, sr)
            label, confidence, meta = await run_in_threadpool(predict, feature_vec)
            explanation = await run_in_threadpool(explain, features, label)
        except Exception as e:
            await websocket.send_json({'status': 'error', 'message': 'Model inference failed: ' + str(e)})
            await websocket.close()
            return

        await websocket.send_json({
            'status': 'success',
            'classification': label,
            'confidenceScore': round(confidence, 4),
            'explanation': explanation
        })

    except WebSocketDisconnect:
        return
    finally:
        try:
            await websocket.close()
        except Exception:
            pass



@app.get('/client')
async def client_page():
    """Serve the browser-based client page for live testing."""
    p = Path(__file__).parent.parent / 'web_client.html'
    if not p.exists():
        raise HTTPException(status_code=404, detail='Client page not found')
    return HTMLResponse(p.read_text(encoding='utf-8'))
