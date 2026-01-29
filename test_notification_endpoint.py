
import requests
import json

url = "http://localhost:8000/bot/notify"

payload = {
    "alert_id": "TEST_001",
    "platform": "telegram",
    "user_id": "VL_TEST_USER", 
    "title": "Telegram Notification Test",
    "summary": "This is a test notification sent from the backend to verify the Telegram integration."
}

try:
    print(f"Sending POST request to {url}...")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(url, json=payload)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Request failed: {e}")
