"""
Simple script to send notification without emoji encoding issues.
"""

import asyncio
import sys
from schemas.vibelets import BotNotification
from services.vibelets_service import push_notification
from helpers import postgresql


async def send_notification(user_id: str, title: str, message: str):
    """Send a notification to Slack"""
    await postgresql.connect()
    
    try:
        print(f"Sending notification to user_id: {user_id}")
        print(f"Title: {title}")
        print(f"Message: {message}")
        print("-" * 70)
        
        payload = BotNotification(
            alert_id=f"test_alert_{user_id}",
            platform="slack",
            user_id=user_id,
            title=title,
            summary=message
        )
        
        result = await push_notification(payload)
        
        print(f"Result: {result}")
        
        if result.get("slack") == "sent":
            print("\nSUCCESS! Notification sent to Slack!")
            return True
        else:
            print(f"\nFAILED: {result.get('slack', 'Unknown error')}")
            return False
    
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await postgresql.disconnect()


if __name__ == "__main__":
    # Default values - change as needed
    USER_ID = "1"  # Change to your user_id
    TITLE = "Test Alert"
    MESSAGE = "This is a test notification from the backend. Your Slack integration is working!"
    
    # Allow command line arguments
    if len(sys.argv) > 1:
        USER_ID = sys.argv[1]
    if len(sys.argv) > 2:
        TITLE = sys.argv[2]
    if len(sys.argv) > 3:
        MESSAGE = sys.argv[3]
    
    success = asyncio.run(send_notification(USER_ID, TITLE, MESSAGE))
    sys.exit(0 if success else 1)
