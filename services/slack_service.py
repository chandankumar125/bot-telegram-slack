from slack_sdk import WebClient
from config import SLACK_BOT_TOKEN
from services.vibelets_service import resolve_query

client = WebClient(token=SLACK_BOT_TOKEN)

def handle_event(payload):
    if payload.type == "url_verification":
        return {"challenge": payload.challenge}
    
    event = payload.event
    if not event:
        return {"ok": True}
    
    # Only process message events
    if event.type != "message":
        return {"ok": True}
    
    # Ignore bot messages to avoid infinite loops
    if hasattr(event, "bot_id") and event.bot_id:
        return {"ok": True}
    
    # Ignore messages without text
    if not event.text:
        return {"ok": True}
    
    # Get user_id from event (use user field if available, otherwise use channel)
    user_id = getattr(event, "user", event.channel)
    
    reply = resolve_query(user_id, event.text)
    send_message(event.channel, reply)
    return {"ok": True}


def send_message(channel_id: str, text: str):
    try:
        client.chat_postMessage(channel=channel_id, text=text)
        return {"ok": True, "status": "sent"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
