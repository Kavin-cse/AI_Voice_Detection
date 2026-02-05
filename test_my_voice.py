"""
Test AI Voice Detection API with Your Own Voice
Method B: Python Script with Full Control
"""

import base64
import requests
import json
import sys
from pathlib import Path

def test_voice(mp3_file, language="English"):
    """Test your voice with the AI Detection API"""
    
    # Configuration
    API_ENDPOINT = "http://localhost:8000/api/voice-detection"
    API_KEY = "testkey"
    
    # Validate file exists
    mp3_path = Path(mp3_file)
    if not mp3_path.exists():
        print(f"❌ ERROR: File not found: {mp3_file}")
        print(f"   Please check the file path and try again.")
        return False
    
    print("\n" + "="*70)
    print("🎤 TESTING YOUR VOICE WITH AI DETECTION API")
    print("="*70)
    
    # Step 1: Read and encode audio
    print(f"\n[1/4] Reading audio file...")
    try:
        with open(mp3_path, 'rb') as f:
            mp3_data = f.read()
        
        file_size_mb = len(mp3_data) / (1024 * 1024)
        print(f"      ✓ File size: {file_size_mb:.2f} MB")
        print(f"      ✓ File: {mp3_path.name}")
    except Exception as e:
        print(f"      ❌ Error reading file: {e}")
        return False
    
    # Step 2: Encode to Base64
    print(f"\n[2/4] Encoding to Base64...")
    try:
        base64_audio = base64.b64encode(mp3_data).decode('ascii')
        print(f"      ✓ Base64 size: {len(base64_audio):,} characters")
        print(f"      ✓ Encoding successful")
    except Exception as e:
        print(f"      ❌ Error encoding: {e}")
        return False
    
    # Step 3: Prepare and send request
    print(f"\n[3/4] Sending request to API...")
    print(f"      Endpoint: {API_ENDPOINT}")
    print(f"      Language: {language}")
    
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "language": language,
        "audioFormat": "mp3",
        "audioBase64": base64_audio
    }
    
    try:
        response = requests.post(
            API_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"      ✓ Response received")
        print(f"      ✓ Status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"      ❌ Connection Error: Cannot reach API")
        print(f"      Make sure API server is running on port 8000")
        return False
    except requests.exceptions.Timeout:
        print(f"      ❌ Timeout: API took too long to respond")
        return False
    except Exception as e:
        print(f"      ❌ Error: {e}")
        return False
    
    # Step 4: Process response
    print(f"\n[4/4] Processing results...")
    
    if response.status_code == 200:
        try:
            result = response.json()
            
            print(f"      ✓ Results received")
            
            # Display formatted results
            print("\n" + "="*70)
            print("🎉 RESULTS")
            print("="*70)
            print(f"Status:          {result.get('status', 'N/A')}")
            print(f"Classification:  {result.get('classification', 'N/A')}")
            print(f"Confidence:      {result.get('confidenceScore', 'N/A')}")
            print(f"Language:        {result.get('language', 'N/A')}")
            print(f"Explanation:     {result.get('explanation', 'N/A')}")
            print("="*70 + "\n")
            
            return True
        
        except json.JSONDecodeError:
            print(f"      ❌ Error: Invalid JSON response")
            print(f"      Response: {response.text}")
            return False
    
    elif response.status_code == 400:
        print(f"      ⚠️  Status 400: Bad Request")
        error_data = response.json()
        print(f"      Error: {error_data.get('message', 'Unknown error')}")
        print(f"      This might mean: Invalid audio format or corrupted file")
        return False
    
    elif response.status_code == 401:
        print(f"      ❌ Status 401: Unauthorized")
        print(f"      API Key is missing or invalid")
        return False
    
    elif response.status_code == 403:
        print(f"      ❌ Status 403: Forbidden")
        print(f"      API Key is rejected")
        return False
    
    else:
        print(f"      ❌ Status {response.status_code}: Error")
        print(f"      Response: {response.text}")
        return False


def main():
    """Main function"""
    
    print("\n" + "="*70)
    print("AI-GENERATED VOICE DETECTION - MANUAL TEST")
    print("="*70)
    
    # Get file path
    print("\nPlease provide your MP3 file path or save a voice recording as MP3 first.")
    print("Examples:")
    print("  - C:\\Users\\kavin\\Downloads\\my_voice.mp3")
    print("  - C:\\temp\\test_audio.mp3")
    
    mp3_file = input("\nEnter MP3 file path: ").strip()
    
    if not mp3_file:
        print("❌ No file path provided.")
        return
    
    # Get language
    languages = ["Tamil", "English", "Hindi", "Malayalam", "Telugu"]
    print("\nAvailable languages:")
    for i, lang in enumerate(languages, 1):
        print(f"  {i}. {lang}")
    
    lang_choice = input("Select language (1-5) [default: 2 - English]: ").strip()
    
    if lang_choice and lang_choice.isdigit() and 1 <= int(lang_choice) <= 5:
        language = languages[int(lang_choice) - 1]
    else:
        language = "English"
        print(f"Using default language: {language}")
    
    # Test the voice
    success = test_voice(mp3_file, language)
    
    if success:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed. Please check your file and try again.")


if __name__ == "__main__":
    main()
