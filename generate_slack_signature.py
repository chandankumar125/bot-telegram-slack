
import hashlib
import hmac
import time
import os
import json
from dotenv import load_dotenv

load_dotenv()

SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

def generate_signature(body_json):
    if not SLACK_SIGNING_SECRET:
        print("Error: SLACK_SIGNING_SECRET not found in .env")
        return

    # 1. Get current timestamp
    timestamp = str(int(time.time()))

    # 2. Prepare the base string
    # Format: v0:{timestamp}:{body}
    sig_basestring = f"v0:{timestamp}:{body_json}"

    # 3. Hash it using HMAC SHA256
    my_signature = "v0=" + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()

    print("\n" + "="*50)
    print("✅ 1. COPY THESE HEADERS INTO POSTMAN")
    print("="*50)
    print(f"X-Slack-Request-Timestamp: {timestamp}")
    print(f"X-Slack-Signature: {my_signature}")
    print("="*50 + "\n")
    
    print("="*50)
    print("✅ 2. COPY THIS EXACT JSON INTO POSTMAN BODY (RAW -> JSON)")
    print("⚠️  The signature above is valid ONLY for this exact content.")
    print("="*50)
    print(body)
    print("="*50 + "\n")

if __name__ == "__main__":
    # Define the payload you want to test here
    payload = {
        "token": "verification_token",
        "team_id": "T123456",
        "api_app_id": "A123456",
        "event": {
            "type": "message",
            "text": "Hello bot, this is a test message!",
            "user": "U123456",
            "channel": "C123456",
            "ts": "1610000000.000100"
        },
        "type": "event_callback"
    }
    
    body = json.dumps(payload, separators=(',', ':')) # Slack uses compact JSON for signatures
    print(f"Payload being signed: {body}")
    generate_signature(body)
