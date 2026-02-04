import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
SLACK_CLIENT_ID = os.getenv("SLACK_CLIENT_ID")
SLACK_CLIENT_SECRET = os.getenv("SLACK_CLIENT_SECRET")
SLACK_REDIRECT_URI = os.getenv("SLACK_REDIRECT_URI", "https://preprod.vibelets.ai/bot/slack/oauth_callback")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_SECRET_TOKEN = os.getenv("TELEGRAM_SECRET_TOKEN", "vibelets_telegram_secret_2026")

WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_APP_SECRET = os.getenv("WHATSAPP_APP_SECRET")

VIBELETS_API_KEY = os.getenv("VIBELETS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
VIBELETS_BASE_URL = os.getenv("VIBELETS_BASE_URL", "https://preprod.vibelets.ai/api")
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:8000/dashboard/")


# Database Configuration
# DB_HOST = os.getenv("DB_HOST", "localhost")
# DB_NAME = os.getenv("DB_NAME", "postgres")
# DB_USER = os.getenv("DB_USER", "postgres")
# DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
# DB_PORT = os.getenv("DB_PORT", "5432")
PG_DATABASE_URL = os.getenv("PG_DATABASE_URL")

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

