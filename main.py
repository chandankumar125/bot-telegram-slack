import os
from dotenv import load_dotenv
from fastapi import FastAPI
from routers import slack, notifications, telegram, whatsapp
from config import VIBELETS_API_KEY, SLACK_BOT_TOKEN, TELEGRAM_BOT_TOKEN, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Vibelets Bot Service")


@app.on_event("startup")
async def startup_event():
    """Check configuration on startup"""
    if not VIBELETS_API_KEY:
        logger.warning("⚠️  VIBELETS_API_KEY is not set. AI query resolution will not work.")
    if not SLACK_BOT_TOKEN:
        logger.warning("⚠️  SLACK_BOT_TOKEN is not set. Slack integration will not work.")
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("⚠️  TELEGRAM_BOT_TOKEN is not set. Telegram integration will not work.")
    if not WHATSAPP_PHONE_NUMBER_ID or not WHATSAPP_ACCESS_TOKEN:
        logger.warning("⚠️  WhatsApp credentials are not set. WhatsApp integration will not work.")


app.include_router(slack.router, prefix="/bot/slack")
app.include_router(telegram.router, prefix="/bot/telegram")
app.include_router(whatsapp.router, prefix="/bot/whatsapp")
app.include_router(notifications.router, prefix="/bot")

@app.get("/health")
def health():
    return {"status": "ok"}
