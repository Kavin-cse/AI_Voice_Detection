import base64
import io
import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from pydub import AudioSegment
import numpy as np

client = TestClient(app)

API_KEY = os.getenv('API_KEY', 'testkey')


def synth_mp3_base64(human=True):
    sr = 16000
    t = np.linspace(0, 1.5, int(sr*1.5), endpoint=False)
    base = 120 if human else 150
    if human:
        jitter = 0.02 * np.sin(2*np.pi*5*t)
        y = 0.5 * np.sin(2*np.pi*(base + jitter)*t) + 0.02 * np.random.randn(len(t))
    else:
        y = 0.5 * np.sin(2*np.pi*base*t) + 0.005*np.random.randn(len(t))
    # make mp3
    buf = io.BytesIO()
    AudioSegment(
        (y * 32767).astype(np.int16).tobytes(),
        frame_rate=sr,
        sample_width=2,
        channels=1
    ).export(buf, format='mp3')
    b64 = base64.b64encode(buf.getvalue()).decode('ascii')
    return b64


def test_missing_api_key():
    payload = {
        'language': 'English',
        'audioFormat': 'mp3',
        'audioBase64': synth_mp3_base64(human=True)
    }
    r = client.post('/api/voice-detection', json=payload)
    assert r.status_code == 401
    assert r.json()['status'] == 'error'


def test_invalid_api_key():
    payload = {
        'language': 'English',
        'audioFormat': 'mp3',
        'audioBase64': synth_mp3_base64(human=True)
    }
    r = client.post('/api/voice-detection', json=payload, headers={'x-api-key': 'bad'})
    assert r.status_code == 403
    assert r.json()['status'] == 'error'


def test_valid_human_request():
    payload = {
        'language': 'English',
        'audioFormat': 'mp3',
        'audioBase64': synth_mp3_base64(human=True)
    }
    r = client.post('/api/voice-detection', json=payload, headers={'x-api-key': API_KEY})
    assert r.status_code == 200
    j = r.json()
    assert j['status'] == 'success'
    assert j['language'] == 'English'
    assert j['classification'] in ['AI_GENERATED', 'HUMAN']
    assert 0.0 <= j['confidenceScore'] <= 1.0
    assert isinstance(j['explanation'], str)
