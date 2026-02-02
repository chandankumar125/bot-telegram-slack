
import requests
import json
import time
import hmac
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

def generate_headers(body_str):
    timestamp = str(int(time.time()))
    sig_basestring = f"v0:{timestamp}:{body_str}"
    signature = "v0=" + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    return {
        "X-Slack-Signature": signature,
        "X-Slack-Request-Timestamp": timestamp,
        "Content-Type": "application/json"
    }

url = "http://localhost:8000/bot/slack/events"

payload = {
    "token": "verification_token",
    "team_id": "T123456",
    "api_app_id": "A123456",
    "event": {
        "type": "message",
        "text": "Self-test message from backend script",
        "user": "U123456",
        "channel": "C123456",
        "ts": "1610000000.000100"
    },
    "type": "event_callback"
}

body_str = json.dumps(payload, separators=(',', ':'))

try:
    print(f"Sending POST to {url}...")
    response = requests.post(url, data=body_str, headers=generate_headers(body_str))
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Failed to connect: {e}")
