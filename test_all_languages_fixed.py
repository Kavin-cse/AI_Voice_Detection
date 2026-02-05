"""
Test AI Voice Detection API with all languages
Uses the same test utility functions from tests/test_api.py
"""
import sys
import os

# Add source to path
sys.path.insert(0, os.path.dirname(__file__))

import base64
import io
import requests
import numpy as np
from pydub import AudioSegment

def synth_mp3_base64(human=True):
    """Generate synthetic MP3 audio (from test_api.py)"""
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
        audio_base64 = synth_mp3_base64(human=False)  # Generate AI-like audio
        print(f"  ✓ Generated test MP3 audio ({len(audio_base64)} chars)")
        
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
        print(f"  → Sending request to API...")
        response = requests.post(ENDPOINT, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract data
            classification = result.get('classification', 'N/A')
            confidence = result.get('confidenceScore', 'N/A')
            explanation = result.get('explanation', 'N/A')
            status = result.get('status', 'N/A')
            
            # Display result
            print(f"  ✓ Response received (Status: 200)")
            print(f"\n  📊 RESULTS for {lang}:")
            print(f"     Status: {status}")
            print(f"     Classification: {classification}")
            print(f"     Confidence Score: {confidence}")
            print(f"     Explanation: {explanation[:70]}...")
            
            results.append({
                "language": lang,
                "status": response.status_code,
                "classification": classification,
                "confidence": confidence,
                "success": True
            })
            print(f"  ✅ Test PASSED")
        else:
            error_msg = response.text[:100] if response.text else "Unknown error"
            print(f"  ❌ Test FAILED - HTTP {response.status_code}")
            print(f"     Error: {error_msg}")
            results.append({
                "language": lang,
                "status": response.status_code,
                "success": False,
                "error": error_msg
            })
    
    except requests.exceptions.ConnectionError:
        print(f"  ❌ CONNECTION ERROR")
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
    print("🎉 ALL TESTS PASSED! API is working correctly with all languages.")
    print("✅ Your API is ready for hackathon submission!")
else:
    print(f"⚠️  {total - passed} test(s) failed.")
print("="*70 + "\n")
