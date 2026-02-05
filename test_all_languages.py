import base64
import io
import numpy as np
import soundfile as sf
import requests
import subprocess
import shutil
import json

def create_test_audio():
    """Create synthetic test audio (AI-generated style) as MP3"""
    sr = 16000
    t = np.linspace(0, 1.0, int(sr*1.0))
    # Pure sine wave (characteristic of AI-generated audio)
    y = 0.5 * np.sin(2*np.pi*150*t)
    # Minimal noise
    y += 0.001 * np.random.randn(len(t))
    
    # Save to WAV buffer
    wav_buf = io.BytesIO()
    sf.write(wav_buf, y, sr, format='WAV')
    wav_data = wav_buf.getvalue()
    
    # Convert WAV to MP3 using ffmpeg
    try:
        proc = subprocess.Popen(
            ['ffmpeg', '-hide_banner', '-loglevel', 'error', 
             '-i', 'pipe:0', '-f', 'mp3', 'pipe:1'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        mp3_data, err = proc.communicate(wav_data)
        if proc.returncode == 0:
            return base64.b64encode(mp3_data).decode('ascii')
        else:
            raise RuntimeError(f"ffmpeg failed: {err.decode()}")
    except FileNotFoundError:
        print("⚠️  ffmpeg not found. Install it for MP3 support.")
        raise

# Configuration
API_KEY = "testkey"
ENDPOINT = "http://localhost:8000/api/voice-detection"
languages = ["Tamil", "English", "Hindi", "Malayalam", "Telugu"]

print("\n" + "="*70)
print("🧪 TESTING AI-GENERATED VOICE DETECTION API - ALL LANGUAGES")
print("="*70)

results = []
for idx, lang in enumerate(languages, 1):
    print(f"\n[{idx}/{len(languages)}] Testing {lang}...")
    
    try:
        # Create test audio
        audio_base64 = create_test_audio()
        print(f"  ✓ Generated test audio ({len(audio_base64)} chars)")
        
        # Prepare request
        payload = {
            "language": lang,
            "audioFormat": "mp3",
            "audioBase64": audio_base64
        }
        
        headers = {
            "x-api-key": API_KEY,
            "Content-Type": "application/json"
        }
        
        # Send request
        print(f"  → Sending request to {ENDPOINT}...")
        response = requests.post(ENDPOINT, json=payload, headers=headers, timeout=10)
        
        print(f"  ✓ Response received (Status: {response.status_code})")
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract data
            classification = result.get('classification', 'N/A')
            confidence = result.get('confidenceScore', 'N/A')
            explanation = result.get('explanation', 'N/A')
            status = result.get('status', 'N/A')
            
            # Display result
            print(f"\n  📊 RESULTS for {lang}:")
            print(f"     Status: {status}")
            print(f"     Classification: {classification}")
            print(f"     Confidence Score: {confidence}")
            print(f"     Explanation: {explanation[:80]}...")
            
            results.append({
                "language": lang,
                "status": response.status_code,
                "classification": classification,
                "confidence": confidence,
                "success": True
            })
            print(f"  ✅ Test PASSED for {lang}")
        else:
            error_msg = response.text[:100]
            print(f"  ❌ Test FAILED - HTTP {response.status_code}")
            print(f"     Error: {error_msg}")
            results.append({
                "language": lang,
                "status": response.status_code,
                "success": False,
                "error": error_msg
            })
    
    except requests.exceptions.ConnectionError:
        print(f"  ❌ CONNECTION ERROR - Cannot reach {ENDPOINT}")
        print(f"     Make sure API server is running on port 8000")
        results.append({
            "language": lang,
            "success": False,
            "error": "Connection refused"
        })
    
    except Exception as e:
        print(f"  ❌ ERROR: {str(e)}")
        results.append({
            "language": lang,
            "success": False,
            "error": str(e)
        })

# Summary
print("\n" + "="*70)
print("📋 SUMMARY")
print("="*70)

passed = sum(1 for r in results if r.get('success', False))
total = len(results)

for r in results:
    status_icon = "✅" if r.get('success') else "❌"
    lang = r['language']
    classification = r.get('classification', 'N/A')
    confidence = r.get('confidence', 'N/A')
    print(f"{status_icon} {lang:12} → {classification:15} (Confidence: {confidence})")

print(f"\n{'='*70}")
print(f"Total: {passed}/{total} tests passed")
if passed == total:
    print("🎉 ALL TESTS PASSED! API is working correctly.")
else:
    print(f"⚠️  {total - passed} test(s) failed. Check API server status.")
print("="*70 + "\n")
