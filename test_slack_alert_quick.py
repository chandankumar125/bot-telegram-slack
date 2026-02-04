"""
Quick test to see why Slack alerts aren't working.

Run: python test_slack_alert_quick.py --user-id YOUR_USER_ID
"""

import asyncio
import sys
import argparse
from schemas.vibelets import BotNotification
from services.vibelets_service import push_notification
from utils.postgres_db import get_slack_connection
from helpers import postgresql


async def main():
    parser = argparse.ArgumentParser(description='Quick test Slack alert')
    parser.add_argument('--user-id', type=str, required=True, help='Vibelets user ID')
    
    args = parser.parse_args()
    
    await postgresql.connect()
    
    try:
        print("="*70)
        print("QUICK SLACK ALERT TEST")
        print("="*70)
        
        # Check connection
        print(f"\n1. Checking connection for user_id: {args.user_id}")
        connection = await get_slack_connection(args.user_id)
        
        if not connection:
            print("❌ User is NOT connected to Slack")
            print("\nTo see connected accounts, run:")
            print("  python send_alert_to_connected_slack.py --list")
            sys.exit(1)
        
        print(f"✅ Connected!")
        print(f"   Slack User ID: {connection.get('slack_user_id')}")
        print(f"   Team: {connection.get('team_name')}")
        print(f"   Connection status: {connection.get('connected')}")
        
        # Check if connection.get("connected") is True
        if not connection.get("connected"):
            print("\n⚠️  WARNING: Connection exists but 'connected' field is False!")
            print("   This might be the issue. The connection might be marked as disconnected.")
        
        # Send notification
        print(f"\n2. Sending test alert...")
        payload = BotNotification(
            alert_id="quick_test_001",
            platform="slack",
            user_id=args.user_id,
            title="🔍 Quick Test Alert",
            summary="Testing if alerts are working. If you see this, it worked!"
        )
        
        result = await push_notification(payload)
        
        print(f"\n3. Result:")
        print(f"   {result}")
        
        if result.get("slack") == "sent":
            print("\n✅ SUCCESS! Alert should appear in Slack.")
            print("   Check your Slack DMs or the channel where the bot can message you.")
        elif "failed" in str(result.get("slack", "")):
            print(f"\n❌ FAILED: {result.get('slack')}")
            print("\nRun the full debug script for more details:")
            print(f"  python debug_slack_alert.py --user-id {args.user_id}")
        elif result.get("status") == "skipped":
            print(f"\n⚠️  SKIPPED: {result.get('reason')}")
            print("\nPossible reasons:")
            print("  - Connection check failed")
            print("  - Platform mismatch")
            print("  - No targets found")
        else:
            print(f"\n❓ UNKNOWN RESULT: {result}")
            print("\nRun the full debug script for more details:")
            print(f"  python debug_slack_alert.py --user-id {args.user_id}")
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        await postgresql.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
