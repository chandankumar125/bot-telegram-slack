import requests
from config import TELEGRAM_BOT_TOKEN
import sys

def set_webhook():
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in .env")
        return

    if len(sys.argv) < 2:
        print("Usage: python set_webhook.py <YOUR_NGROK_URL>")
        print("Example: python set_webhook.py https://a1b2-c3d4.ngrok-free.app")
        return

    ngrok_url = sys.argv[1].strip().rstrip("/")
    webhook_url = f"{ngrok_url}/bot/telegram/webhook"
    
    print(f"Setting Webhook to: {webhook_url} ...")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={webhook_url}"
    
    try:
        response = requests.get(url)
        print("Response from Telegram:", response.json())
        
        if response.status_code == 200 and response.json().get("ok"):
            print("\n✅ SUCCESS! Webhook is set.")
            print("Telegram will now push messages to your uvicorn server.")
            print("You can STOP the 'test_telegram_polling.py' script now.")
        else:
            print("\n❌ FAILED. Check the error message above.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    set_webhook()
