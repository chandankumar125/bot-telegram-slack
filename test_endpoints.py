import requests
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, payload=None):
    url = f"{BASE_URL}{endpoint}"
    print(f"Testing {method} {url}...", end=" ")
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=payload)
        
        print(f"Status: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"ERROR: {str(e)}")
    print("-" * 30)

print("Waiting for server to ensure it is ready...")
time.sleep(2) 

print("Starting connectivity tests...")

# 1. Health Check
test_endpoint("GET", "/health")

# 2. Telegram Webhook Info
test_endpoint("GET", "/bot/telegram/webhook")

# 3. Slack Events Info
test_endpoint("GET", "/bot/slack/events")

# 4. Notify Info
test_endpoint("GET", "/bot/notify")

print("\nStarting functionality tests...")

# 5. Notify POST (Telegram)
payload_tg = {
    "alert_id": "test-123",
    "platform": "telegram",
    "channel_id": "123456789", 
    "title": "Test Alert Telegram",
    "summary": "This is a test notification for Telegram."
}
test_endpoint("POST", "/bot/notify", payload_tg)

# 6. Notify POST (Slack)
payload_slack = {
    "alert_id": "test-456",
    "platform": "slack",
    "channel_id": "C12345678", 
    "title": "Test Alert Slack",
    "summary": "This is a test notification for Slack."
}
test_endpoint("POST", "/bot/notify", payload_slack)
