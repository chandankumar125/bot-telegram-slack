from fastapi import APIRouter, Request, BackgroundTasks, HTTPException, Depends
import json
from services.telegram_service import handle_update, get_bot_username, send_message
from utils.postgres_db import disconnect_telegram_connection, get_telegram_connection
from schemas.telegram import TelegramUpdate
from utils.auth import get_current_user, create_state_token
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/webhook")
async def telegram_webhook(update: TelegramUpdate, background_tasks: BackgroundTasks):
    """
    Receives Webhook updates from Telegram.
    """
    # Process update in background to ensure fast response to Telegram
    # access .dict() or .model_dump() depending on pydantic version, sticking to dict() for compatibility usually
    payload = update.dict(by_alias=True)
    background_tasks.add_task(handle_update, payload)
    
    return {"ok": True}

@router.get("/connect")
async def connect_link(user_id: str = Depends(get_current_user)):
    """
    Generates a deep link for the user to start the bot and connect their account.
    """
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id")
        
    try:
        username = await get_bot_username()
        state = create_state_token(user_id)
        link = f"https://t.me/{username}?start={state}"
        
        print("\n" + "="*50)
        print(f"STAGE 1: Telegram Connect Link Generated")
        print("-" * 50)
        print(json.dumps({
            "User ID (Vibelets)": user_id,
            "Bot Username": username,
            "Generated Link": link
        }, indent=2))
        print("="*50 + "\n")
        
        return {"url": link}
    except Exception as e:
        logger.error(f"Failed to generate Telegram link: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/disconnect")
async def disconnect_bot(user_id: str = Depends(get_current_user)):
    """
    Disconnects the user from Telegram.
    """
    # Notify User
    conn = get_telegram_connection(user_id)
    if conn and conn.get("connected"):
        chat_id = conn.get("chat_id")
        try:
             await send_message(
                chat_id, 
                f"⚠️ *You have been disconnected.*\n"
                f"👉 [Click here to Connect](http://127.0.0.1:8000/dashboard/)"
             )
        except Exception as e:
            logger.warning(f"Failed to send disconnect message: {e}")

    success = disconnect_telegram_connection(user_id)
    return {"ok": success}

@router.get("/status")
def get_status(user_id: str = Depends(get_current_user)):
    conn = get_telegram_connection(user_id)
    if conn and conn.get("connected"):
        return {"connected": True, "username": conn.get("username")}
    return {"connected": False}
