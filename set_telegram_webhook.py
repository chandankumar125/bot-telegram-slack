import sys
import asyncio
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN

async def set_webhook(domain):
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in .env")
        return

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    url = f"{domain}/bot/telegram/webhook"
    print(f"Setting webhook to: {url}")
    
    try:
        success = await bot.set_webhook(url=url)
        if success:
            print("Webhook set successfully!")
        else:
            print("Failed to set webhook.")
            
        info = await bot.get_webhook_info()
        print(f"Current Webhook Info: {info}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python set_telegram_webhook.py <YOUR_DOMAIN>")
        print("Example: python set_telegram_webhook.py https://my-bot.ngrok.io")
        sys.exit(1)
        
    domain = sys.argv[1].rstrip("/")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(set_webhook(domain))
