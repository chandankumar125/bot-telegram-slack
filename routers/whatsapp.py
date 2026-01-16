from fastapi import APIRouter, Request, Query, HTTPException
from schemas.whatsapp import WhatsAppWebhook
from services.whatsapp_service import handle_webhook, verify_webhook
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/webhook")
async def whatsapp_webhook_verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """Verify WhatsApp webhook (required for initial setup)"""
    try:
        if not hub_mode or not hub_verify_token or not hub_challenge:
            logger.warning("Missing webhook verification parameters")
            raise HTTPException(status_code=403, detail="Missing verification parameters")
        
        challenge = verify_webhook(hub_mode, hub_verify_token, hub_challenge)
        if challenge:
            logger.info("WhatsApp webhook verification successful")
            return int(challenge)  # WhatsApp expects integer response
        else:
            logger.warning("WhatsApp webhook verification failed")
            raise HTTPException(status_code=403, detail="Verification failed")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"WhatsApp webhook verification error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Verification error")

@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    """Handle WhatsApp webhook updates"""
    try:
        body = await request.json()
        logger.info(f"WHATSAPP UPDATE: {json.dumps(body, indent=2)}")
        print(f"WHATSAPP UPDATE: {json.dumps(body, indent=2)}")
        
        # Use raw body directly - WhatsApp webhook structure
        result = handle_webhook(body)
        
        logger.info(f"WHATSAPP RESPONSE: {result}")
        return result
    except Exception as e:
        logger.error(f"WHATSAPP WEBHOOK ERROR: {str(e)}", exc_info=True)
        print(f"WHATSAPP WEBHOOK ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"ok": False, "error": str(e)}

@router.get("/webhook/info")
def whatsapp_webhook_info():
    """Get webhook info (for debugging)"""
    from config import WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN, WHATSAPP_VERIFY_TOKEN
    
    return {
        "phone_number_id": WHATSAPP_PHONE_NUMBER_ID if WHATSAPP_PHONE_NUMBER_ID else "Not set",
        "access_token": "Set" if WHATSAPP_ACCESS_TOKEN else "Not set",
        "verify_token": WHATSAPP_VERIFY_TOKEN if WHATSAPP_VERIFY_TOKEN else "Not set",
        "api_url": f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages" if WHATSAPP_PHONE_NUMBER_ID else "Not available"
    }
