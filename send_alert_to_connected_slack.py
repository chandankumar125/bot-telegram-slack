"""
Send an alert message to a connected Slack account.

This script will:
1. Find connected Slack accounts (or use provided user_id)
2. Send a test alert notification to Slack

Usage:
    python send_alert_to_connected_slack.py --user-id 123
    python send_alert_to_connected_slack.py --user-id 123 --title "Campaign Alert" --message "Your campaign needs attention"
    python send_alert_to_connected_slack.py --list  # List all connected accounts
"""

import asyncio
import sys
import argparse
from schemas.vibelets import BotNotification
from services.vibelets_service import push_notification
from utils.postgres_db import get_slack_connection
from helpers import postgresql


async def list_connected_accounts():
    """List all connected Slack accounts"""
    try:
        sql = """
            SELECT 
                suc.user_id,
                suc.slack_user_id,
                suc.slack_email,
                suc.slack_username,
                sw.team_name,
                sw.team_id,
                suc.connected_at
            FROM public.slack_user_connections suc
            JOIN public.slack_workspaces sw ON sw.id = suc.workspace_id
            WHERE suc.is_connected = TRUE
            ORDER BY suc.connected_at DESC
        """
        rows = await postgresql.query(sql)
        
        if not rows:
            print("No connected Slack accounts found.")
            return []
        
        print("\n" + "="*70)
        print("Connected Slack Accounts:")
        print("="*70)
        for i, row in enumerate(rows, 1):
            print(f"\n{i}. User ID: {row.get('user_id')}")
            print(f"   Slack User ID: {row.get('slack_user_id')}")
            print(f"   Email: {row.get('slack_email', 'N/A')}")
            print(f"   Username: {row.get('slack_username', 'N/A')}")
            print(f"   Team: {row.get('team_name')} ({row.get('team_id')})")
            print(f"   Connected: {row.get('connected_at')}")
        
        print("\n" + "="*70)
        return rows
    
    except Exception as e:
        print(f"Error listing accounts: {e}")
        import traceback
        traceback.print_exc()
        return []


async def send_alert_to_user(user_id: str, title: str = None, message: str = None):
    """Send an alert to a specific user by their Vibelets user_id"""
    # Check if user is connected
    connection = await get_slack_connection(user_id)
    
    if not connection:
        print(f"❌ Error: User ID {user_id} is not connected to Slack.")
        print("\nConnected accounts:")
        await list_connected_accounts()
        return False
    
    print(f"\n✅ Found connected Slack account:")
    print(f"   Slack User ID: {connection.get('slack_user_id')}")
    print(f"   Email: {connection.get('email', 'N/A')}")
    print(f"   Team: {connection.get('team_name')}")
    print("-" * 70)
    
    # Create notification payload
    payload = BotNotification(
        alert_id=f"test_alert_{user_id}_{asyncio.get_event_loop().time()}",
        platform="slack",
        user_id=user_id,
        title=title or "🚨 Test Alert",
        summary=message or "This is a test alert message from your Vibelets backend. Your Slack account is connected and working!"
    )
    
    print(f"\nSending alert notification...")
    print(f"Title: {payload.title}")
    print(f"Message: {payload.summary}")
    print("-" * 70)
    
    result = await push_notification(payload)
    
    print(f"\nResult: {result}")
    
    if result.get("slack") == "sent":
        print("\n✅ Alert sent successfully to Slack!")
        return True
    else:
        print(f"\n❌ Failed to send alert: {result.get('slack', 'Unknown error')}")
        return False


async def main():
    parser = argparse.ArgumentParser(description='Send alert message to connected Slack account')
    parser.add_argument('--user-id', type=str, help='Vibelets user ID to send alert to')
    parser.add_argument('--title', type=str, default=None, help='Alert title (default: "🚨 Test Alert")')
    parser.add_argument('--message', type=str, default=None, help='Alert message (default: test message)')
    parser.add_argument('--list', action='store_true', help='List all connected Slack accounts')
    
    args = parser.parse_args()
    
    # Connect to database
    await postgresql.connect()
    
    try:
        if args.list:
            # List all connected accounts
            await list_connected_accounts()
        
        elif args.user_id:
            # Send alert to specific user
            success = await send_alert_to_user(args.user_id, args.title, args.message)
            sys.exit(0 if success else 1)
        
        else:
            # Interactive mode: list accounts and let user choose
            print("No user_id provided. Listing connected accounts...\n")
            accounts = await list_connected_accounts()
            
            if accounts:
                print("\nTo send an alert, use:")
                print(f"  python send_alert_to_connected_slack.py --user-id <user_id>")
                print(f"\nExample:")
                if accounts:
                    example_id = accounts[0].get('user_id')
                    print(f"  python send_alert_to_connected_slack.py --user-id {example_id}")
            else:
                print("\nNo connected accounts found.")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        await postgresql.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
