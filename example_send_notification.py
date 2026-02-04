"""
Simple example showing how to send a notification to Slack from backend code.

This demonstrates using the push_notification function directly.
"""

import asyncio
from schemas.vibelets import BotNotification
from services.vibelets_service import push_notification
from helpers import postgresql


async def example_send_notification_to_user():
    """Example: Send notification to a user by their Vibelets user_id"""
    # Connect to database first
    await postgresql.connect()
    
    try:
        # Create notification payload
        payload = BotNotification(
            alert_id="alert_12345",
            platform="slack",  # or "all" to send to all connected platforms
            user_id="123",  # Replace with actual Vibelets user ID
            title="Campaign Alert",
            summary="Your campaign 'Summer Sale' has exceeded the daily budget limit."
        )
        
        result = await push_notification(payload)
        
        print("Notification Result:")
        print(result)
        
        if result.get("slack") == "sent":
            print("✅ Notification sent to Slack successfully!")
        else:
            print(f"❌ Failed: {result}")
    
    finally:
        await postgresql.disconnect()


async def example_send_notification_to_channel():
    """Example: Send notification directly to a Slack channel/user ID"""
    # Connect to database first
    await postgresql.connect()
    
    try:
        # Create notification payload with direct channel_id
        payload = BotNotification(
            alert_id="alert_12345",
            platform="slack",
            channel_id="U1234567890",  # Replace with actual Slack user ID or channel ID
            title="System Notification",
            summary="This is a direct notification sent to a specific Slack channel/user."
        )
        
        result = await push_notification(payload)
        
        print("Notification Result:")
        print(result)
        
        if result.get("slack") == "sent":
            print("✅ Notification sent successfully!")
        else:
            print(f"❌ Failed: {result}")
    
    finally:
        await postgresql.disconnect()


async def example_send_to_all_platforms():
    """Example: Send notification to all connected platforms (Slack, Telegram, WhatsApp)"""
    # Connect to database first
    await postgresql.connect()
    
    try:
        # Create notification payload for all platforms
        payload = BotNotification(
            alert_id="alert_12345",
            platform="all",  # Send to all connected platforms
            user_id="123",  # Replace with actual Vibelets user ID
            title="Important Update",
            summary="Your account has been updated. Please review the changes."
        )
        
        result = await push_notification(payload)
        
        print("Notification Result:")
        print(result)
        
        # Check which platforms received the notification
        for platform, status in result.items():
            if status == "sent":
                print(f"✅ Sent to {platform}")
            else:
                print(f"❌ {platform}: {status}")
    
    finally:
        await postgresql.disconnect()


# Run examples
if __name__ == "__main__":
    print("Example 1: Send notification to user by Vibelets user_id")
    print("-" * 50)
    # Uncomment to run:
    # asyncio.run(example_send_notification_to_user())
    
    print("\nExample 2: Send notification directly to Slack channel/user")
    print("-" * 50)
    # Uncomment to run:
    # asyncio.run(example_send_notification_to_channel())
    
    print("\nExample 3: Send notification to all platforms")
    print("-" * 50)
    # Uncomment to run:
    # asyncio.run(example_send_to_all_platforms())
