from fastapi import APIRouter
from schemas.telegram import TelegramWebhook
from services.telegram_service import handle_message

router = APIRouter()

@router.post("/webhook")
def telegram_webhook(payload: TelegramWebhook):
    return handle_message(payload)

@router.get("/webhook")
def telegram_webhook_info():
    return {"ok": True}


