import requests
from config import WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN, WHATSAPP_VERIFY_TOKEN
from services.vibelets_service import resolve_query
import logging

logger = logging.getLogger(__name__)

def get_whatsapp_api_url():
    """Get WhatsApp Graph API URL"""
    if not WHATSAPP_PHONE_NUMBER_ID or not WHATSAPP_ACCESS_TOKEN:
        return None
    return f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"

def handle_webhook(webhook_data):
    """Handle incoming WhatsApp webhook"""
    try:
        # WhatsApp sends webhooks in entry array
        if not webhook_data.get("entry"):
            logger.debug("No entry in webhook")
            return {"ok": True}
        
        for entry in webhook_data.get("entry", []):
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                
                # Handle incoming messages
                messages = value.get("messages", [])
                if messages:
                    for message in messages:
                        handle_message(message, value.get("contacts", []))
                
                # Handle status updates (message delivery status)
                statuses = value.get("statuses", [])
                if statuses:
                    for status in statuses:
                        logger.debug(f"Message status update: {status}")
        
        return {"ok": True}
    except Exception as e:
        logger.error(f"Error handling WhatsApp webhook: {str(e)}", exc_info=True)
        return {"ok": False, "error": str(e)}

def handle_message(message, contacts=None):
    """Handle individual WhatsApp message"""
    try:
        # Only process text messages
        if message.get("type") != "text":
            logger.debug(f"Ignoring non-text message type: {message.get('type')}")
            return
        
        text_obj = message.get("text")
        if not text_obj or not text_obj.get("body"):
            logger.debug("Message has no text body")
            return
        
        # Get sender phone number (WhatsApp ID)
        from_number = message.get("from")
        if not from_number:
            logger.warning("Message has no 'from' field")
            return
        
        # Get message text
        text = text_obj.get("body")
        
        # Get contact name if available
        contact_name = None
        if contacts:
            for contact in contacts:
                if contact.get("wa_id") == from_number:
                    profile = contact.get("profile", {})
                    contact_name = profile.get("name")
                    break
        
        user_id = from_number  # Use phone number as user_id
        logger.info(f"Processing WhatsApp message from {from_number} ({contact_name}): {text}")
        print(f"Processing WhatsApp message from {from_number} ({contact_name}): {text}")
        
        # Process query and get response
        reply = resolve_query(user_id, text)
        
        logger.info(f"Sending reply to {from_number}: {reply}")
        print(f"Sending reply to {from_number}: {reply}")
        
        # Send response back to user
        send_message(from_number, reply)
        
    except Exception as e:
        logger.error(f"Error handling WhatsApp message: {str(e)}", exc_info=True)

def send_message(to: str, text: str):
    """Send message via WhatsApp Business API"""
    api_url = get_whatsapp_api_url()
    if not api_url:
        logger.error("WhatsApp API URL not available - check credentials")
        return {"ok": False, "error": "WhatsApp credentials not set"}
    
    if not WHATSAPP_ACCESS_TOKEN:
        logger.error("WHATSAPP_ACCESS_TOKEN is not set")
        return {"ok": False, "error": "WHATSAPP_ACCESS_TOKEN is not set"}
    
    try:
        response = requests.post(
            api_url,
            headers={
                "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {
                    "body": text
                }
            },
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        logger.info(f"WhatsApp message sent: {result}")
        return {"ok": True, "result": result}
    except requests.exceptions.HTTPError as e:
        error_detail = "Unknown error"
        try:
            error_detail = e.response.json()
        except:
            error_detail = str(e)
        logger.error(f"WhatsApp API error: {error_detail}")
        return {"ok": False, "error": str(error_detail)}
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        return {"ok": False, "error": str(e)}

def verify_webhook(mode, token, challenge):
    """Verify WhatsApp webhook (for initial setup)"""
    # Debug logging
    logger.info(f"Webhook verification attempt: mode={mode}, token_length={len(token) if token else 0}, expected_length={len(WHATSAPP_VERIFY_TOKEN) if WHATSAPP_VERIFY_TOKEN else 0}")
    
    if not WHATSAPP_VERIFY_TOKEN:
        logger.error("WHATSAPP_VERIFY_TOKEN is not set in .env file")
        return None
    
    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
        logger.info("WhatsApp webhook verified successfully")
        return challenge
    else:
        # More detailed logging
        token_match = token == WHATSAPP_VERIFY_TOKEN
        logger.warning(f"WhatsApp webhook verification failed:")
        logger.warning(f"  mode={mode} (expected: 'subscribe')")
        logger.warning(f"  token matches={token_match}")
        logger.warning(f"  received token: '{token}'")
        logger.warning(f"  expected token: '{WHATSAPP_VERIFY_TOKEN}'")
        logger.warning(f"  token lengths: received={len(token) if token else 0}, expected={len(WHATSAPP_VERIFY_TOKEN)}")
        return None
