"""
Simple example showing how to send a message to Slack from backend code.

This demonstrates the three main ways to send messages:
1. send_message_to_user() - Send to a user by their Slack user ID
2. send_message() - Send with token and channel ID
3. send_notification() - Send using team_id and channel_id
"""

import asyncio
from services.slack_service import send_message_to_user, send_message, send_notification
from helpers import postgresql


async def example_send_to_user():
    """Example: Send a message to a Slack user by their Slack user ID"""
    # Connect to database first
    await postgresql.connect()
    
    try:
        # Replace with actual Slack user ID (e.g., "U1234567890")
        slack_user_id = "U1234567890"
        message = "Hello! This is a test message from the backend."
        
        result = await send_message_to_user(slack_user_id, message)
        
        if result.get("ok"):
            print("✅ Message sent successfully!")
        else:
            print(f"❌ Error: {result.get('error')}")
    
    finally:
        await postgresql.disconnect()


async def example_send_to_channel():
    """Example: Send a message to a channel using token and channel ID"""
    # Connect to database first
    await postgresql.connect()
    
    try:
        # Replace with actual values
        token = "xoxb-your-token-here"
        channel_id = "C1234567890"  # Channel ID or user ID for DM
        message = "Hello channel! This is a test message."
        
        result = send_message(token, channel_id, message)
        
        if result.get("ok"):
            print("✅ Message sent successfully!")
        else:
            print(f"❌ Error: {result.get('error')}")
    
    finally:
        await postgresql.disconnect()


async def example_send_notification():
    """Example: Send a notification using team_id and channel_id"""
    # Connect to database first
    await postgresql.connect()
    
    try:
        # Replace with actual values
        team_id = "T1234567890"
        channel_id = "C1234567890"  # Channel ID or user ID for DM
        message = "📢 Notification: This is a test notification."
        
        result = await send_notification(team_id, channel_id, message)
        
        if result.get("ok"):
            print("✅ Notification sent successfully!")
        else:
            print(f"❌ Error: {result.get('error')}")
    
    finally:
        await postgresql.disconnect()


# Run examples
if __name__ == "__main__":
    print("Example 1: Send to user by Slack user ID")
    print("-" * 50)
    # Uncomment to run:
    # asyncio.run(example_send_to_user())
    
    print("\nExample 2: Send to channel with token")
    print("-" * 50)
    # Uncomment to run:
    # asyncio.run(example_send_to_channel())
    
    print("\nExample 3: Send notification")
    print("-" * 50)
    # Uncomment to run:
    # asyncio.run(example_send_notification())
