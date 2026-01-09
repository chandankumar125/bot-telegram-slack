from slack_sdk import WebClient
from config import SLACK_BOT_TOKEN
from services.vibelets_service import resolve_query

client = WebClient(token=SLACK_BOT_TOKEN)

def handle_event(payload):
    if payload.type == "url_verification":
        return {"challenge": payload.challenge}
    
    event = payload.event
    if not event or not event.text:
        return {"ok": True}
    
    reply = resolve_query(event.channel, event.text)
    send_message(event.channel, reply)
    return {"ok": True}

def send_message(channel_id: str, text: str):
    try:
        client.chat_postMessage(channel=channel_id, text=text)
        return {"ok": True, "status": "sent"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
