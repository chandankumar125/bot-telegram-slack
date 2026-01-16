from fastapi import APIRouter, Request
from schemas.telegram import TelegramUpdate
from services.telegram_service import handle_update
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/webhook")
async def telegram_webhook(request: Request):
    """Handle Telegram webhook updates"""
    try:
        body = await request.json()
        logger.info(f"TELEGRAM UPDATE: {json.dumps(body, indent=2)}")
        print(f"TELEGRAM UPDATE: {json.dumps(body, indent=2)}")
        
        # Use raw body directly to avoid Pydantic field name issues
        # Telegram sends "from" which is a Python keyword
        result = handle_update(body)
        
        logger.info(f"TELEGRAM RESPONSE: {result}")
        return result
    except Exception as e:
        logger.error(f"TELEGRAM WEBHOOK ERROR: {str(e)}", exc_info=True)
        print(f"TELEGRAM WEBHOOK ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"ok": False, "error": str(e)}

@router.get("/webhook")
def telegram_webhook_info():
    """Get webhook info"""
    from services.telegram_service import get_webhook_info
    return get_webhook_info()

@router.post("/set-webhook")
async def set_telegram_webhook(request: Request):
    """Set Telegram webhook URL"""
    from services.telegram_service import set_webhook
    data = await request.json()
    url = data.get("url")
    if not url:
        return {"ok": False, "error": "URL is required"}
    return set_webhook(url)
