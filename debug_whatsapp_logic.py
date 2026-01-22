import sys
import os
import traceback
import asyncio
import logging

# Configure logging to stdout
logging.basicConfig(level=logging.INFO)

# Add current dir to sys.path
sys.path.append(os.getcwd())

from services.whatsapp_service import handle_incoming_message
from schemas.whatsapp import WhatsAppWebhookPayload

# Mock Payload
payload_dict = {
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

payload = WhatsAppWebhookPayload(**payload_dict)

print("Starting debug...")
try:
    result = handle_incoming_message(payload)
    print("Result:", result)
except Exception:
    traceback.print_exc()
