import requests
import json
import time

URL = "http://localhost:8000/bot/whatsapp/webhook"

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
    response = requests.post(URL, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Failed to connect: {e}")
