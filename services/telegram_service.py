import requests
from config import TELEGRAM_BOT_TOKEN
from services.vibelets_service import resolve_query
import logging

logger = logging.getLogger(__name__)

def get_telegram_api_url():
    """Get Telegram API URL with token"""
    if not TELEGRAM_BOT_TOKEN:
        return None
    return f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def handle_update(update):
    """Handle incoming Telegram update (message)"""
    if not update.get("message"):
        logger.debug("No message in update")
        return {"ok": True}
    
    message = update["message"]
    
    # Ignore messages without text
    if not message.get("text"):
        logger.debug("Message has no text")
        return {"ok": True}
    
    # Get user and chat info
    # Telegram API sends "from" field
    from_user = message.get("from")
    if not from_user:
        logger.warning(f"Message has no 'from' field. Message keys: {list(message.keys())}")
        logger.warning(f"Full message: {message}")
        return {"ok": True}
    
    user_id = str(from_user.get("id"))
    chat_id = str(message["chat"]["id"])
    text = message["text"]
    
    logger.info(f"Processing message from user {user_id} in chat {chat_id}: {text}")
    print(f"Processing message from user {user_id} in chat {chat_id}: {text}")
    
    # Process query and get response
    reply = resolve_query(user_id, text)
    
    logger.info(f"Sending reply to chat {chat_id}: {reply}")
    print(f"Sending reply to chat {chat_id}: {reply}")
    
    # Send response back to user
    send_message(chat_id, reply)
    return {"ok": True}


def send_message(chat_id: str, text: str):
    """Send message to Telegram chat"""
    api_url = get_telegram_api_url()
    if not api_url:
        return {"ok": False, "error": "TELEGRAM_BOT_TOKEN is not set"}
    
    try:
        response = requests.post(
            f"{api_url}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            },
            timeout=10
        )
        response.raise_for_status()
        return {"ok": True, "status": "sent"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def set_webhook(url: str):
    """Set Telegram webhook URL"""
    api_url = get_telegram_api_url()
    if not api_url:
        return {"ok": False, "error": "TELEGRAM_BOT_TOKEN is not set"}
    
    try:
        response = requests.post(
            f"{api_url}/setWebhook",
            json={"url": url},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}


def get_webhook_info():
    """Get current webhook info"""
    api_url = get_telegram_api_url()
    if not api_url:
        return {"ok": False, "error": "TELEGRAM_BOT_TOKEN is not set"}
    
    try:
        response = requests.get(
            f"{api_url}/getWebhookInfo",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}
