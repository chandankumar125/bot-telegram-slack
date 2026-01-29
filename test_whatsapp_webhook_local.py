import requests
import json
import time

import hmac
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

# Match the port to your running Uvicorn server (default 8000)
URL = "http://localhost:8000/bot/whatsapp/webhook"
SECRET = os.getenv("WHATSAPP_APP_SECRET", "adsparkx_whatsapp_app_secret_2026")

# 1. Sample Payload (Text Message)
payload = {
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "1003796069475756",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "15555555555",
              "phone_number_id": "1003796069475756"
            },
            "contacts": [
              {
                "profile": {
                  "name": "Test User"
                },
                "wa_id": "16315551234"
              }
            ],
            "messages": [
              {
                "from": "16315551234",
                "id": "wamid.HBgLMTYzMTU1NTEyMzQVAgARGBI5QTNDQTVCM0Q0Q0Q2RTY3RTcA",
                "timestamp": "1688665000",
                "text": {
                  "body": "Hello World"
                },
                "type": "text"
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}

print("Testing WhatsApp Webhook...")

try:
    # Calculate Signature
    payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    signature = hmac.new(SECRET.encode('utf-8'), payload_bytes, hashlib.sha256).hexdigest()
    
    headers = {
        "X-Hub-Signature-256": f"sha256={signature}",
        "Content-Type": "application/json"
    }

    response = requests.post(URL, data=payload_bytes, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Failed to connect: {e}")
