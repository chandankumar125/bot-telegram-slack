import logging
import json
from telegram import Bot, Update
from telegram.constants import ParseMode
from config import TELEGRAM_BOT_TOKEN
from services.vibelets_service import resolve_query
from utils.postgres_db import get_telegram_user_by_chat_id, save_telegram_connection, get_telegram_connection
from helpers.telegram_api import send_telegram_message as send_telegram_msg_helper
from utils.auth import verify_state_token

import asyncio

logger = logging.getLogger(__name__)

# Initialize Bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)
BOT_USERNAME = None

async def get_bot_username():
    global BOT_USERNAME
    if not BOT_USERNAME:
        me = await bot.get_me()
        BOT_USERNAME = me.username
    return BOT_USERNAME

async def handle_update(payload: dict):
    """
    Handle incoming Telegram updates from Webhook.
    """
    try:
        update = Update.de_json(payload, bot)
    except Exception as e:
        logger.error(f"Failed to parse update: {e}")
        return

    # Only handle messages
    if not update.message or not update.message.text:
        return

    await process_telegram_message(update.message)

async def process_telegram_message(message):
    chat_id = message.chat_id
    text = message.text.strip()
    user = message.from_user
    username = user.username if user else None
    first_name = user.first_name if user else None
    last_name = user.last_name if user else None

    logger.info(f"Received Telegram message from {chat_id}: {text}")

    # 1. Handle Commands
    if text.startswith("/start"):
        # Check for deep linking parameter (signed vibelets_user_id)
        params = text.split(" ")
        if len(params) > 1:
            state = params[1]
            vibelets_user_id = verify_state_token(state)
            
            if not vibelets_user_id:
                logger.warning(f"Invalid or expired Telegram start token: {state}")
                await send_message(chat_id, "❌ *Link Failed*: The connection link is invalid or has expired. Please generate a new link from the dashboard.")
                return

            print("\n" + "="*50)
            print(f"STAGE 2: Received Callback/Start from Telegram (Verified)")
            print("-" * 50)
            print(json.dumps({
                "User ID (Vibelets)": vibelets_user_id,
                "Telegram User": username,
                "Chat ID": chat_id,
                "First Name": first_name
            }, indent=2))
            print("="*50 + "\n")

            save_telegram_connection(vibelets_user_id, str(chat_id), username, first_name, last_name)
            response_text = (
                f"👋 *Hello! I'm the Vibelets Bot.*\n"
                f"✅ *You are now successfully connected!*\n"
                f"I can help you with insights about your ad campaigns.\n\n"
                f"• Ask me questions like _'How is my campaign performing?'_\n"
            )
            await send_message(chat_id, response_text)
            return
        
        # If no param, check if already connected
        existing_user = get_telegram_user_by_chat_id(str(chat_id))
        if existing_user:
            await send_message(chat_id, "👋 Welcome back! You are already connected. How can I help you?")
        else:
            await send_message(
                chat_id, 
                f"⚠️ *Account Not Connected*\n"
                f"You need to link your Vibelets account to use this bot.\n"
                f"👉 [Click here to Connect](http://127.0.0.1:8000/dashboard/)"
            )
        return

    if text.startswith("/help"):
        await send_message(chat_id, "Just ask me any question about your campaigns!")
        return

    # 2. Check Connection:  identifying the user for authentication
    vibelets_user_id = get_telegram_user_by_chat_id(str(chat_id))
    if not vibelets_user_id:
        await send_message(chat_id, "⚠️ Please connect your account first using the /start command with your connection token.")
        return

    # 3. Resolve Query
    # Run sync resolve_query in a thread to keep async loop unblocked
    try:
        loop = asyncio.get_event_loop()
        reply = await loop.run_in_executor(None, resolve_query, vibelets_user_id, text)
        await send_message(chat_id, reply)
    except Exception as e:
        logger.error(f"Error resolving query: {e}")
        await send_message(chat_id, "Sorry, I encountered an issue processing your request.")

async def send_message(chat_id: str, text: str):
    try:
        # Offload sync helper to thread
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, 
            lambda: send_telegram_msg_helper(chat_id, text, parse_mode="Markdown")
        )
    except Exception as e:
        logger.warning(f"Markdown send failed, trying plain text: {e}")
        try:
           loop = asyncio.get_event_loop()
           await loop.run_in_executor(
                None, 
                lambda: send_telegram_msg_helper(chat_id, text, parse_mode=None)
            )
        except Exception as e2:
             logger.error(f"Failed to send Telegram message: {e2}")

async def send_notification(vibelets_user_id: str, text: str):
    """
    Sends a proactive notification to a specific user.
    """
    connection = get_telegram_connection(vibelets_user_id)
    if connection and connection.get("connected"):
        chat_id = connection.get("chat_id")
        await send_message(chat_id, text)
        return {"ok": True}
    return {"ok": False, "error": "User not connected to Telegram"}

async def send_channel_broadcast(channel_username_or_id: str, text: str):
    """
    Sends a message to a public Telegram Channel.
    The Bot must be an Admin in the channel.
    channel_username_or_id: e.g. "@MyChannel" or "-100123456789"
    """
    return await send_message(channel_username_or_id, text)
