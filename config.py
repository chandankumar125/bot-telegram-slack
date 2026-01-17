import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
SLACK_CLIENT_ID = os.getenv("SLACK_CLIENT_ID")
SLACK_CLIENT_SECRET = os.getenv("SLACK_CLIENT_SECRET")
SLACK_REDIRECT_URI = os.getenv("SLACK_REDIRECT_URI", "https://preprod.vibelets.ai/bot/slack/oauth_callback")

VIBELETS_API_KEY = os.getenv("VIBELETS_API_KEY")
VIBELETS_BASE_URL = os.getenv("VIBELETS_BASE_URL", "https://preprod.vibelets.ai/api")

