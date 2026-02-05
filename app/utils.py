import base64
import io
import subprocess
import shutil
import numpy as np
import soundfile as sf


def decode_mp3_to_wav_bytes(mp3_bytes: bytes, target_sr: int = 16000):
    # Try pydub first (may fail in some environments due to pyaudioop missing)
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(io.BytesIO(mp3_bytes), format='mp3')
        audio = audio.set_frame_rate(target_sr).set_channels(1)
        buf = io.BytesIO()
        audio.export(buf, format='wav')
        buf.seek(0)
        return buf.read()
    except Exception:
        # Fallback: use ffmpeg subprocess if available
        if shutil.which('ffmpeg') is None:
            raise RuntimeError('Neither pydub nor ffmpeg are available to decode mp3')
        proc = subprocess.Popen(
            ['ffmpeg','-hide_banner','-loglevel','error','-i','pipe:0','-f','wav','-ar',str(target_sr),'-ac','1','pipe:1','-y'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out, err = proc.communicate(mp3_bytes)
        if proc.returncode != 0:
            raise RuntimeError('ffmpeg failed to decode mp3')
        return out


def load_wav_np(wav_bytes: bytes):
    data, sr = sf.read(io.BytesIO(wav_bytes))
    # ensure mono
    if data.ndim > 1:
        data = data.mean(axis=1)
    return data.astype(np.float32), sr


def b64_to_wav_np(audio_base64: str):
    try:
        mp3_bytes = base64.b64decode(audio_base64)
    except Exception as e:
        raise ValueError('Invalid base64 audio data')
    # Try mp3-specific decode first, then fall back to a general ffmpeg-based converter
    try:
        wav_bytes = decode_mp3_to_wav_bytes(mp3_bytes)
    except Exception:
        # Use ffmpeg to convert arbitrary input formats (webm/ogg/opus/etc.) to wav
        if shutil.which('ffmpeg') is None:
            raise RuntimeError('Neither pydub nor ffmpeg are available to decode audio')
        proc = subprocess.Popen(
            ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', 'pipe:0', '-f', 'wav', '-ar', str(16000), '-ac', '1', 'pipe:1', '-y'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out, err = proc.communicate(mp3_bytes)
        if proc.returncode != 0:
            raise RuntimeError('ffmpeg failed to decode audio')
        wav_bytes = out
    return load_wav_np(wav_bytes)
