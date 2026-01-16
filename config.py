import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# WhatsApp Business API credentials
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")  # For webhook verification

VIBELETS_API_KEY = os.getenv("VIBELETS_API_KEY")
VIBELETS_BASE_URL = "https://preprod.vibelets.ai/api"

