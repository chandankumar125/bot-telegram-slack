import sys
import os
import asyncio

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.telegram_service import send_message
from utils.postgres_db import get_telegram_connection

async def test_alert():
    user_id = 1 # Using a numeric ID common in your DB schema
    
    print(f"Fetching connection details for user_id={user_id}...")
    connection = get_telegram_connection(user_id)
    
    if not connection or not connection.get("connected"):
        print("❌ User is not connected to Telegram.")
        return

    chat_id = connection.get("chat_id")
    
    print(f"✅ Found Connection: Chat ID {chat_id}")
    print("🚀 Sending test alert...")
    
    try:
        await send_message(
            chat_id=chat_id,
            text="🚀 *Test Alert*: If you see this, the Telegram notification system is working perfectly!"
        )
        print("Result: {'ok': True, 'status': 'sent'}")
    except Exception as e:
        print(f"Result: {'ok': False, 'error': str(e)}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_alert())
