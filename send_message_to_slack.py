"""
Script to send a message from backend to Slack.

Usage examples:
1. Send to a specific Slack user by their Slack user ID:
   python send_message_to_slack.py --user-id U123456 --message "Hello from backend!"

2. Send to a channel with token and channel ID:
   python send_message_to_slack.py --token xoxb-... --channel C123456 --message "Hello channel!"

3. Send notification using team_id and channel_id:
   python send_message_to_slack.py --team-id T123456 --channel C123456 --message "Notification"
"""

import asyncio
import sys
import argparse
from services.slack_service import send_message_to_user, send_message, send_notification
from helpers import postgresql


async def main():
    parser = argparse.ArgumentParser(description='Send a message to Slack from backend')
    parser.add_argument('--user-id', type=str, help='Slack user ID (e.g., U123456)')
    parser.add_argument('--channel', type=str, help='Slack channel ID (e.g., C123456)')
    parser.add_argument('--token', type=str, help='Slack bot token')
    parser.add_argument('--team-id', type=str, help='Slack team ID (e.g., T123456)')
    parser.add_argument('--message', type=str, required=True, help='Message text to send')
    
    args = parser.parse_args()
    
    if not args.message:
        print("Error: --message is required")
        sys.exit(1)
    
    # Connect to database
    await postgresql.connect()
    
    try:
        # Method 1: Send to user by Slack user ID (recommended)
        if args.user_id:
            print(f"Sending message to Slack user {args.user_id}...")
            result = await send_message_to_user(args.user_id, args.message)
            if result.get("ok"):
                print("✅ Message sent successfully!")
                print(f"Response: {result}")
            else:
                print(f"❌ Failed to send message: {result.get('error')}")
                sys.exit(1)
        
        # Method 2: Send to channel with token
        elif args.token and args.channel:
            print(f"Sending message to channel {args.channel}...")
            result = send_message(args.token, args.channel, args.message)
            if result.get("ok"):
                print("✅ Message sent successfully!")
                print(f"Response: {result}")
            else:
                print(f"❌ Failed to send message: {result.get('error')}")
                sys.exit(1)
        
        # Method 3: Send notification using team_id
        elif args.team_id and args.channel:
            print(f"Sending notification to team {args.team_id}, channel {args.channel}...")
            result = await send_notification(args.team_id, args.channel, args.message)
            if result.get("ok"):
                print("✅ Message sent successfully!")
                print(f"Response: {result}")
            else:
                print(f"❌ Failed to send message: {result.get('error')}")
                sys.exit(1)
        
        else:
            print("Error: You must provide one of the following combinations:")
            print("  --user-id <slack_user_id>")
            print("  --token <token> --channel <channel_id>")
            print("  --team-id <team_id> --channel <channel_id>")
            sys.exit(1)
    
    finally:
        await postgresql.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
