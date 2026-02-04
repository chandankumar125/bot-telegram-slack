"""
Script to send a notification to Slack from backend.

Usage examples:
1. Send notification to a user by their Vibelets user_id:
   python send_notification_to_slack.py --user-id 123 --title "Alert" --summary "Your campaign needs attention"

2. Send notification directly to a Slack user/channel:
   python send_notification_to_slack.py --channel-id U123456 --title "Alert" --summary "Your campaign needs attention"

3. Send to all platforms (Slack, Telegram, WhatsApp):
   python send_notification_to_slack.py --user-id 123 --platform all --title "Alert" --summary "Your campaign needs attention"
"""

import asyncio
import sys
import argparse
from schemas.vibelets import BotNotification
from services.vibelets_service import push_notification
from helpers import postgresql


async def main():
    parser = argparse.ArgumentParser(description='Send a notification to Slack from backend')
    parser.add_argument('--user-id', type=str, help='Vibelets user ID (e.g., 123)')
    parser.add_argument('--channel-id', type=str, help='Slack channel/user ID (e.g., U123456 or C123456)')
    parser.add_argument('--platform', type=str, default='slack', 
                        choices=['slack', 'telegram', 'whatsapp', 'all'],
                        help='Platform to send to (default: slack)')
    parser.add_argument('--title', type=str, required=True, help='Notification title')
    parser.add_argument('--summary', type=str, required=True, help='Notification summary/message')
    parser.add_argument('--alert-id', type=str, default='test_alert_001', help='Alert ID (default: test_alert_001)')
    
    args = parser.parse_args()
    
    if not args.user_id and not args.channel_id:
        print("Error: You must provide either --user-id or --channel-id")
        sys.exit(1)
    
    # Connect to database
    await postgresql.connect()
    
    try:
        # Create notification payload
        payload = BotNotification(
            alert_id=args.alert_id,
            platform=args.platform,
            user_id=args.user_id,
            channel_id=args.channel_id,
            title=args.title,
            summary=args.summary
        )
        
        print(f"Sending notification to {args.platform}...")
        print(f"Title: {args.title}")
        print(f"Summary: {args.summary}")
        print("-" * 50)
        
        result = await push_notification(payload)
        
        print("Result:")
        print(result)
        
        # Check if notification was sent successfully
        if result.get("slack") == "sent" or any(v == "sent" for v in result.values()):
            print("\n✅ Notification sent successfully!")
        elif result.get("status") == "skipped":
            print(f"\n⚠️  Notification skipped: {result.get('reason')}")
        else:
            print("\n❌ Failed to send notification")
            for platform, status in result.items():
                if "failed" in str(status):
                    print(f"  {platform}: {status}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        await postgresql.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
