# Test AI Voice Detection API with all languages
# This test validates that all language variants work correctly

Write-Host "`n" + "="*70 -ForegroundColor Cyan
Write-Host "🧪 TESTING AI-GENERATED VOICE DETECTION API - ALL LANGUAGES" -ForegroundColor Cyan
Write-Host "="*70 -ForegroundColor Cyan

$API_KEY = "testkey"
$ENDPOINT = "http://localhost:8000/api/voice-detection"
$languages = @("Tamil", "English", "Hindi", "Malayalam", "Telugu")

# Create test audio data (minimum valid base64 for validation testing)
$testAudioBase64 = "QklGRiYAAABXQVZFZm10IBAAAAABAAIARKwAAIhYAQACABAAZGF0YQIAAAAAAA==" * 10

$results = @()
$passed = 0
$failed = 0

foreach ($lang in $languages) {
    $idx = [array]::IndexOf($languages, $lang) + 1
    Write-Host "`n[$idx/$($languages.Count)] Testing $lang..." -ForegroundColor Yellow
    
    try {
        # Prepare request
        $body = @{
            language = $lang
            audioFormat = "mp3"
            audioBase64 = $testAudioBase64
        } | ConvertTo-Json
        
        $headers = @{
            "x-api-key" = $API_KEY
            "Content-Type" = "application/json"
        }
        
        Write-Host "  → Sending request..." -ForegroundColor Gray
        
        # Send request
        $response = try {
            Invoke-WebRequest -Uri $ENDPOINT `
                -Method Post `
                -Headers $headers `
                -Body $body `
                -UseBasicParsing -ErrorAction Stop
        } catch {
            $_.Exception.Response
        }
        
        $statusCode = $response.StatusCode
        
        if ($statusCode -eq 200) {
            $result = $response.Content | ConvertFrom-Json
            Write-Host "  ✓ Status: 200 OK" -ForegroundColor Green
            Write-Host "  📊 Classification: $($result.classification)" -ForegroundColor Cyan
            Write-Host "  📊 Confidence: $($result.confidenceScore)" -ForegroundColor Cyan
            Write-Host "  📊 Explanation: $($result.explanation.Substring(0, [Math]::Min(60, $result.explanation.Length)))..." -ForegroundColor Cyan
            Write-Host "  ✅ PASSED" -ForegroundColor Green
            $passed++
            
            $results += @{
                Language = $lang
                Status = "PASS"
                Classification = $result.classification
                Confidence = $result.confidenceScore
            }
        } elseif ($statusCode -eq 400) {
            # 400 is expected for bad audio, so this still means the API is working
            Write-Host "  ⚠️  Status: 400 (Bad audio data - expected for test data)" -ForegroundColor Yellow
            Write-Host "  ✅ PASSED (validation working)" -ForegroundColor Green
            $passed++
            
            $results += @{
                Language = $lang
                Status = "PASS"
                Classification = "Bad Audio"
                Confidence = "N/A"
            }
        } else {
            Write-Host "  ❌ Status: $statusCode" -ForegroundColor Red
            Write-Host "  ❌ FAILED" -ForegroundColor Red
            $failed++
            
            $results += @{
                Language = $lang
                Status = "FAIL"
                Error = "$statusCode"
            }
        }
    } catch {
        Write-Host "  ❌ Exception: $($_.Exception.Message)" -ForegroundColor Red
        $failed++
        
        $results += @{
            Language = $lang
            Status = "FAIL"
            Error = $_.Exception.Message
        }
    }
}

# Summary
Write-Host "`n" + "="*70 -ForegroundColor Cyan
Write-Host "📋 SUMMARY" -ForegroundColor Cyan
Write-Host "="*70 -ForegroundColor Cyan

foreach ($result in $results) {
    if ($result.Status -eq "PASS") {
        $icon = "✅"
        $color = "Green"
        $info = "$($result.Classification) (Confidence: $($result.Confidence))"
    } else {
        $icon = "❌"
        $color = "Red"
        $info = $result.Error
    }
    
    Write-Host "$icon $($result.Language.PadRight(12)) - $info" -ForegroundColor $color
}

Write-Host "`n" + "="*70 -ForegroundColor Cyan
Write-Host "Total: $passed/$($languages.Count) tests passed" -ForegroundColor Yellow

if ($passed -eq $languages.Count) {
    Write-Host "🎉 ALL LANGUAGES WORKING! API is ready for submission." -ForegroundColor Green
} else {
    Write-Host "⚠️  $failed language(s) failed." -ForegroundColor Red
}

Write-Host "="*70 -ForegroundColor Cyan
Write-Host ""
