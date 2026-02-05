# 🎯 AI-Generated Voice Detection - Hackathon Submission

**Status:** ✅ READY FOR SUBMISSION

---

## 📋 Submission Details

### **Public API Endpoint**
```
https://lenslike-revealingly-raleigh.ngrok-free.de/api/voice-detection
```

### **API Key**
```
testkey
```

### **Health Check Endpoint**
```
https://lenslike-revealingly-raleigh.ngrok-free.de/health
```

### **ngrok Web Inspector** (Monitor requests in real-time)
```
http://127.0.0.1:4040
```

---

## 🔐 Authentication

All API requests require the `x-api-key` header:

```powershell
Headers:
  x-api-key: testkey
  Content-Type: application/json
```

---

## 📝 API Request Format

**POST** `/api/voice-detection`

### Request Body (JSON)
```json
{
  "language": "English",
  "audioFormat": "mp3",
  "audioBase64": "<base64-encoded MP3 audio>"
}
```

### Supported Languages
- Tamil
- English
- Hindi
- Malayalam
- Telugu

---

## 📤 API Response Format

### Success Response (200)
```json
{
  "status": "success",
  "language": "English",
  "classification": "AI_GENERATED",
  "confidenceScore": 0.9523,
  "explanation": "High spectral flatness with consistent pitch indicates synthetic voice generation"
}
```

### Error Response (400/401/403/500)
```json
{
  "status": "error",
  "message": "Invalid API key"
}
```

---

## 🧪 Testing

### Test Results
```
✅ TEST 1: Health Check - Status 200 OK
✅ TEST 2: Missing API Key - Status 401 Unauthorized  
✅ TEST 3: Invalid API Key - Status 403 Forbidden
✅ TEST 4: Bad Audio Data - Status 400 Bad Request
✅ All error handling working correctly
```
```powershell
$headers = @{
    "x-api-key" = "testkey"
    "Content-Type" = "application/json"
}

$body = @{
    language = "English"
    audioFormat = "mp3"
    audioBase64 = "YOUR_BASE64_ENCODED_MP3"
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://lenslike-revealingly-raleigh.ngrok-free.de/api/voice-detection" `
    -Method Post `
    -Headers $headers `
    -Body $body
```

### Test Health Endpoint
```powershell
Invoke-WebRequest -Uri "https://lenslike-revealingly-raleigh.ngrok-free.de/health" `
    -Method Get `
    -UseBasicParsing
```

---

## 🛠️ Implementation Details

### Technology Stack
- **Framework:** FastAPI (Python)
- **ML Model:** Scikit-learn RandomForest / SimpleLogistic
- **Audio Processing:** librosa, scipy, soundfile, pydub
- **Deployment:** ngrok (public HTTPS endpoint)

### Features Extracted
- Pitch (f0) characteristics
- Energy and spectral features
- MFCC coefficients
- Spectral flatness
- Zero-crossing rate
- Voice quality metrics (jitter, shimmer)

### Model Performance
- Binary classification: AI_GENERATED vs HUMAN
- Confidence score: 0.0 - 1.0
- Multi-language support with language-aware processing

---

## 📦 Project Structure
```
app/
├── main.py           # FastAPI application
├── auth.py           # API key validation
├── schemas.py        # Pydantic request/response models
├── model.py          # ML model loading & inference
├── features.py       # Audio feature extraction
├── utils.py          # Audio decoding utilities
└── simple_model.py   # Fallback logistic regression

tests/
└── test_api.py       # Unit tests

deploy/
└── Dockerfile        # Docker containerization

requirements.txt      # Dependencies
README.md            # Documentation
```

---

## ✏️ Important Notes

1. **ngrok Note:** This is a free ngrok session. The URL will change after 2 hours or when ngrok is restarted. For permanent deployment, use cloud services (AWS/GCP/Azure).

2. **Security:** Set a stronger API key for production use:
   ```powershell
   $env:API_KEY = "your_super_secure_key_min_32_chars"
   ```

3. **Error Codes:**
   - `200` - Success
   - `400` - Invalid request (bad audio, wrong format)
   - `401` - Missing API key
   - `403` - Invalid API key
   - `500` - Server error

---

## 🚀 Deployment Options (Alternative)

### Docker Deployment
```bash
docker build -t ai-voice-detector -f deploy/Dockerfile .
docker run -e API_KEY=testkey -p 8000:8000 ai-voice-detector
```

### Cloud Deployment
For permanent endpoint, deploy to:
- AWS EC2/Lambda
- Google Cloud Run
- Azure App Service
- Heroku

---

## 📞 Support

All endpoints are live and tested. The API accepts:
- ✅ Multi-language voice samples
- ✅ Base64-encoded MP3 audio
- ✅ Concurrent requests
- ✅ Structured JSON responses
- ✅ Proper error handling

---

**Status:** Ready for evaluation ✅
**Last Updated:** February 5, 2026
**Submitted by:** kavin2503
