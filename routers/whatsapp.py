from fastapi import APIRouter, Request, HTTPException, Query, BackgroundTasks, Header
from services.whatsapp_service import handle_incoming_message
from config import WHATSAPP_VERIFY_TOKEN, WHATSAPP_APP_SECRET
from utils.db import get_whatsapp_connection, disconnect_whatsapp_connection
from helpers.whatsapp_api import verify_whatsapp_signature
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/webhook")
def verify_webhook(
    mode: str = Query(..., alias="hub.mode"),
    token: str = Query(..., alias="hub.verify_token"),
    challenge: str = Query(..., alias="hub.challenge"),
):
    """
    Verifies the webhook subscription with Meta.
    """
    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
        logger.info("WhatsApp webhook verified successfully!")
        return int(challenge)
    
    logger.warning("WhatsApp webhook verification failed.")
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/webhook")
async def receive_webhook(
    request: Request, 
    background_tasks: BackgroundTasks,
    x_hub_signature: str = Header(None, alias="X-Hub-Signature-256")
):
    """
    Receives incoming WhatsApp messages.
    """
    try:
        body_bytes = await request.body()
        body_str = body_bytes.decode('utf-8')
        
        if WHATSAPP_APP_SECRET and x_hub_signature:
            if not verify_whatsapp_signature(body_str, x_hub_signature, WHATSAPP_APP_SECRET):
                logger.warning("Invalid WhatsApp signature")
                raise HTTPException(status_code=401, detail="Invalid signature")

        import json
        from schemas.whatsapp import WhatsAppWebhookPayload
        
        try:
            payload_data = json.loads(body_str)
        except json.JSONDecodeError:
             raise HTTPException(status_code=400, detail="Invalid JSON")

        # Basic validation to check if it's a WhatsApp object using Pydantic
        try:
            payload = WhatsAppWebhookPayload(**payload_data)
        except Exception as e:
            # If schema validation fails, it might be a different kind of event (e.g. status update with different structure)
            # or just malformed. We'll log it and return 200 to acknowledge receipt to Meta to stop retries.
            logger.warning(f"Schema validation failed (ignoring event): {e}")
            return {"status": "ignored"}

        if payload.object == "whatsapp_business_account":
            # Process in background
            background_tasks.add_task(handle_incoming_message, payload)
            return {"status": "ok"}
        else:
            raise HTTPException(status_code=404, detail="Not a WhatsApp event")
            
    except Exception as e:
        logger.error(f"Error reading WhatsApp webhook: {e}")
        raise HTTPException(status_code=400, detail="Server Error")

@router.get("/status")
def get_connection_status(user_id: str):
    """
    Checks if the user is connected to WhatsApp.
    """
    connection = get_whatsapp_connection(user_id)
    if connection and connection.get("connected"):
        return {
            "connected": True, 
            "whatsapp_id": connection.get("whatsapp_id"),
            "name": connection.get("name")
        }
    return {"connected": False}

@router.post("/disconnect")
def disconnect_bot(user_id: str):
    """
    Disconnects the user from WhatsApp.
    """
    success = disconnect_whatsapp_connection(user_id)
    if success:
        return {"ok": True, "message": "Disconnected successfully"}
    return {"ok": False, "message": "User not connected or user not found"}

@router.get("/connect")
def get_connect_link(user_id: str):
    """
    Returns the WhatsApp Deep Link to start a chat and connect.
    NOTE: In production, you'd replace 'PHONE_NUMBER' with your actual bot number.
    Since we don't have the Bot Number in config easily (only ID), 
    we might need to hardcode it or add it to env.
    For now, I'll use a placeholder or assume the user sets WHATSAPP_BOT_NUMBER in env.
    """
    import os
    # Default to a placeholder if not set. 
    # USER MUST SET THIS IN .ENV: WHATSAPP_BOT_NUMBER=15550239485
    bot_number = os.getenv("WHATSAPP_BOT_NUMBER", "15551609511") 
    
    # Sanitize number: remove +, -, spaces
    import re
    clean_number = re.sub(r'[^0-9]', '', bot_number)
    
    text = f"Connect {user_id}"
    link = f"https://wa.me/{clean_number}?text={text}"
    
    return {"link": link}
