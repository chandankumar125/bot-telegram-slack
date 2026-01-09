import requests
from config import TELEGRAM_BOT_TOKEN
from services.vibelets_service import resolve_query

def handle_message(payload):
    if not payload.message or not payload.message.text:
        return {"ok": True}

    chat_id = payload.message.chat.id
    text = payload.message.text

    reply = resolve_query(str(chat_id), text)
    send_message(chat_id, reply)
    return {"ok": True}

def send_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={"chat_id": chat_id, "text": text})
        return response.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}
