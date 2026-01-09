import requests
from config import VIBELETS_BASE_URL, VIBELETS_API_KEY

def resolve_query(user_id, question):
    try:
        response = requests.post(
            f"{VIBELETS_BASE_URL}/bot/resolve",
            headers={"Authorization": f"Bearer {VIBELETS_API_KEY}"},
            json={"user_id": user_id, "question": question},
            timeout=10
        )
        response.raise_for_status()
        return response.json().get("answer", "No response found")
    except Exception as e:
        return f"Error connecting to Vibelets AI: {str(e)}"

def push_notification(payload):
    msg = f"*{payload.title}*\n{payload.summary}"
    
    if payload.platform == "slack":
        from services.slack_service import send_message as slack_send_message
        return slack_send_message(payload.channel_id, msg)
    
    elif payload.platform == "telegram":
        from services.telegram_service import send_message as telegram_send_message
        return telegram_send_message(int(payload.channel_id), msg)
    
    return {"status": "failed", "reason": "Unsupported platform"}
