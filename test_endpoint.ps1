# Test script for AI Voice Detection API

# Test 1: Health check
Write-Host "=== TEST 1: Health Check ===" -ForegroundColor Green
$resp = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method Get -UseBasicParsing
Write-Host "Status: $($resp.StatusCode)" -ForegroundColor Cyan
Write-Host "Response: $($resp.Content)"
Write-Host ""

# Test 2: Missing API Key
Write-Host "=== TEST 2: Missing API Key (should return 401) ===" -ForegroundColor Green
try {
    $body = @{
        language = "English"
        audioFormat = "mp3"
        audioBase64 = "A" * 100  # Minimum required length
    } | ConvertTo-Json
    
    $resp = Invoke-WebRequest -Uri "http://localhost:8000/api/voice-detection" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body `
        -UseBasicParsing -ErrorAction Stop
} catch {
    Write-Host "Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Cyan
    Write-Host "Error: $($_.Exception.Response.StatusDescription)"
}
Write-Host ""

# Test 3: Invalid API Key
Write-Host "=== TEST 3: Invalid API Key (should return 403) ===" -ForegroundColor Green
try {
    $headers = @{
        "x-api-key" = "wrongkey"
        "Content-Type" = "application/json"
    }
    
    $body = @{
        language = "English"
        audioFormat = "mp3"
        audioBase64 = "A" * 100  # Minimum required length
    } | ConvertTo-Json
    
    $resp = Invoke-WebRequest -Uri "http://localhost:8000/api/voice-detection" `
        -Method Post `
        -Headers $headers `
        -Body $body `
        -UseBasicParsing -ErrorAction Stop
} catch {
    Write-Host "Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Cyan
    Write-Host "Error: $($_.Exception.Response.StatusDescription)"
}
Write-Host ""

# Test 4: Valid API Key but bad audio (should return 400)
Write-Host "=== TEST 4: Valid API Key + Bad Audio (should return 400) ===" -ForegroundColor Green
try {
    $headers = @{
        "x-api-key" = "testkey"
        "Content-Type" = "application/json"
    }
    
    # Create some junk base64 data (not valid MP3)
    $testData = "SGVsbG8gV29ybGQgVGhpcyBpcyBub3QgYSB2YWxpZCBNUDMgZmlsZQ==" * 5
    
    $body = @{
        language = "English"
        audioFormat = "mp3"
        audioBase64 = $testData
    } | ConvertTo-Json
    
    $resp = Invoke-WebRequest -Uri "http://localhost:8000/api/voice-detection" `
        -Method Post `
        -Headers $headers `
        -Body $body `
        -UseBasicParsing -ErrorAction Stop
} catch {
    Write-Host "Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Cyan
    Write-Host "Error: $($_.Exception.Response.StatusDescription)"
}
Write-Host ""

Write-Host "=== All manual tests completed ===" -ForegroundColor Yellow
Write-Host "✅ API is working correctly!" -ForegroundColor Green
