import logging
import asyncio
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from services.telegram_service import process_telegram_message
from config import TELEGRAM_BOT_TOKEN

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def wrapper(update, context):
    """Wraps the PTB update to call our service logic"""
    if update.message:
        await process_telegram_message(update.message)

def main():
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found!")
        return

    print("Starting Telegram Bot in Polling Mode (Local Testing)...")
    
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Handle all text messages
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), wrapper))
    # Handle commands
    app.add_handler(MessageHandler(filters.COMMAND, wrapper))

    print("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == '__main__':
    main()
