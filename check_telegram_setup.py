"""
Check if your Telegram bot is properly configured
"""
import requests
from config import TELEGRAM_BOT_TOKEN

print("="*60)
print("Telegram Bot Setup Checker")
print("="*60)
print()

if not TELEGRAM_BOT_TOKEN:
    print("ERROR: TELEGRAM_BOT_TOKEN is not set!")
    print()
    print("Please set it in your .env file:")
    print("   TELEGRAM_BOT_TOKEN=your-token-here")
    print()
    print("To get your token:")
    print("   1. Open Telegram and search for @BotFather")
    print("   2. Send /newbot command")
    print("   3. Follow the prompts to create your bot")
    print("   4. Copy the token BotFather gives you")
    print("   5. Add it to your .env file")
    exit(1)

print("TELEGRAM_BOT_TOKEN is set")
print()

try:
    # Test the token by calling getMe API
    response = requests.get(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe",
        timeout=10
    )
    response.raise_for_status()
    data = response.json()
    
    if data.get("ok"):
        bot_info = data.get("result", {})
        
        print("="*60)
        print("SUCCESS: Telegram Bot is properly configured!")
        print("="*60)
        print()
        print(f"Bot Name:     {bot_info.get('first_name', 'N/A')}")
        print(f"Bot Username: @{bot_info.get('username', 'N/A')}")
        print(f"Bot ID:       {bot_info.get('id', 'N/A')}")
        print(f"Can Join Groups: {bot_info.get('can_join_groups', 'N/A')}")
        print(f"Can Read All Group Messages: {bot_info.get('can_read_all_group_messages', 'N/A')}")
        print()
        print("="*60)
        print("To use this bot:")
        print("="*60)
        print(f"   1. Search for @{bot_info.get('username', 'your_bot')} on Telegram")
        print("   2. Start a conversation")
        print("   3. Send a message to test")
        print()
        print("To set webhook:")
        print("   curl -X POST \"https://api.telegram.org/bot{}/setWebhook\" \\".format(TELEGRAM_BOT_TOKEN))
        print("     -d \"url=https://your-ngrok-url.ngrok.io/bot/telegram/webhook\"")
        print()
        
        # Check webhook status
        webhook_response = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo",
            timeout=10
        )
        if webhook_response.status_code == 200:
            webhook_data = webhook_response.json()
            if webhook_data.get("ok"):
                webhook_info = webhook_data.get("result", {})
                webhook_url = webhook_info.get("url", "")
                if webhook_url:
                    print("="*60)
                    print("Webhook Status:")
                    print("="*60)
                    print(f"   URL: {webhook_url}")
                    print(f"   Pending Updates: {webhook_info.get('pending_update_count', 0)}")
                    print(f"   Last Error: {webhook_info.get('last_error_message', 'None')}")
                    print()
                else:
                    print("="*60)
                    print("Webhook Status:")
                    print("="*60)
                    print("   WARNING: Webhook is NOT set")
                    print("   You need to set a webhook to receive messages")
                    print()
    else:
        print("="*60)
        print("ERROR: Invalid response from Telegram API")
        print("="*60)
        print()
        print(f"Response: {data}")
        print()
        
except requests.exceptions.RequestException as e:
    print("="*60)
    print("ERROR: Cannot connect to Telegram API")
    print("="*60)
    print()
    print(f"Error: {str(e)}")
    print()
    print("Possible issues:")
    print("   1. TELEGRAM_BOT_TOKEN is incorrect")
    print("   2. No internet connection")
    print("   3. Telegram API is down")
    print()
    print("To fix:")
    print("   1. Verify your token with @BotFather")
    print("   2. Make sure token is correct in .env file")
    print("   3. Check your internet connection")
    print()
except Exception as e:
    print("="*60)
    print("ERROR: Unexpected error")
    print("="*60)
    print()
    print(f"Error: {str(e)}")
    print()
