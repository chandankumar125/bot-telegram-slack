"""
Debug script to diagnose why Slack alerts are not being received.

This script will check:
1. User connection status
2. Token validity
3. Message sending process
4. Any errors in the flow
"""

import asyncio
import sys
import argparse
from schemas.vibelets import BotNotification
from services.vibelets_service import push_notification
from services.slack_service import send_message_to_user, get_token_for_team
from utils.postgres_db import get_slack_connection, get_connection_by_slack_user_id
from helpers import postgresql
from helpers.slack_api import publish_slack_message
import logging

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def debug_user_connection(user_id: str):
    """Debug user's Slack connection"""
    print("\n" + "="*70)
    print("STEP 1: Checking User Connection")
    print("="*70)
    
    connection = await get_slack_connection(user_id)
    
    if not connection:
        print(f"❌ User ID {user_id} is NOT connected to Slack")
        return None
    
    print(f"✅ User is connected!")
    print(f"   Vibelets User ID: {user_id}")
    print(f"   Slack User ID: {connection.get('slack_user_id')}")
    print(f"   Email: {connection.get('email', 'N/A')}")
    print(f"   Team Name: {connection.get('team_name')}")
    print(f"   Team ID: {connection.get('team_id')}")
    print(f"   Bot User ID: {connection.get('bot_user_id')}")
    print(f"   Connected: {connection.get('connected')}")
    
    return connection


async def debug_token(team_id: str):
    """Debug token validity"""
    print("\n" + "="*70)
    print("STEP 2: Checking Token Validity")
    print("="*70)
    
    token = await get_token_for_team(team_id)
    
    if not token:
        print(f"❌ No token found for team_id: {team_id}")
        return None
    
    print(f"✅ Token found!")
    print(f"   Token prefix: {token[:20]}...")
    print(f"   Token length: {len(token)}")
    
    return token


async def debug_slack_user_lookup(slack_user_id: str):
    """Debug Slack user lookup"""
    print("\n" + "="*70)
    print("STEP 3: Checking Slack User Lookup")
    print("="*70)
    
    connection = await get_connection_by_slack_user_id(slack_user_id)
    
    if not connection:
        print(f"❌ No connection found for slack_user_id: {slack_user_id}")
        return None
    
    print(f"✅ Connection found!")
    print(f"   Team ID: {connection.get('team_id')}")
    print(f"   Bot User ID: {connection.get('bot_user_id')}")
    print(f"   Has Access Token: {'Yes' if connection.get('access_token') else 'No'}")
    
    return connection


async def test_direct_message(token: str, slack_user_id: str, message: str):
    """Test sending a message directly"""
    print("\n" + "="*70)
    print("STEP 4: Testing Direct Message Send")
    print("="*70)
    
    try:
        print(f"Sending message to {slack_user_id}...")
        print(f"Message: {message}")
        
        result = publish_slack_message(token, slack_user_id, message)
        
        print(f"✅ Message sent successfully!")
        print(f"   Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send message: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_notification_flow(user_id: str):
    """Test the full notification flow"""
    print("\n" + "="*70)
    print("STEP 5: Testing Full Notification Flow")
    print("="*70)
    
    payload = BotNotification(
        alert_id="debug_test_001",
        platform="slack",
        user_id=user_id,
        title="🔍 Debug Test Alert",
        summary="This is a test alert to debug the notification system."
    )
    
    print(f"Payload:")
    print(f"   Alert ID: {payload.alert_id}")
    print(f"   Platform: {payload.platform}")
    print(f"   User ID: {payload.user_id}")
    print(f"   Title: {payload.title}")
    print(f"   Summary: {payload.summary}")
    
    try:
        result = await push_notification(payload)
        print(f"\nResult: {result}")
        
        if result.get("slack") == "sent":
            print("✅ Notification flow completed successfully!")
            return True
        else:
            print(f"❌ Notification flow failed: {result.get('slack', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception in notification flow: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def debug_send_message_to_user(slack_user_id: str, message: str):
    """Debug send_message_to_user function"""
    print("\n" + "="*70)
    print("STEP 6: Testing send_message_to_user Function")
    print("="*70)
    
    try:
        result = await send_message_to_user(slack_user_id, message)
        print(f"Result: {result}")
        
        if result.get("ok"):
            print("✅ send_message_to_user succeeded!")
            return True
        else:
            print(f"❌ send_message_to_user failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception in send_message_to_user: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    parser = argparse.ArgumentParser(description='Debug Slack alert delivery issues')
    parser.add_argument('--user-id', type=str, required=True, help='Vibelets user ID to debug')
    parser.add_argument('--test-message', type=str, default="🔍 Debug test message", help='Test message to send')
    
    args = parser.parse_args()
    
    # Connect to database
    await postgresql.connect()
    
    try:
        print("\n" + "="*70)
        print("SLACK ALERT DEBUGGING TOOL")
        print("="*70)
        print(f"Debugging user_id: {args.user_id}")
        print("="*70)
        
        # Step 1: Check user connection
        connection = await debug_user_connection(args.user_id)
        if not connection:
            print("\n❌ Cannot proceed - user is not connected")
            sys.exit(1)
        
        slack_user_id = connection.get('slack_user_id')
        team_id = connection.get('team_id')
        
        # Step 2: Check token
        token = await debug_token(team_id)
        if not token:
            print("\n❌ Cannot proceed - no valid token")
            sys.exit(1)
        
        # Step 3: Check Slack user lookup
        slack_conn = await debug_slack_user_lookup(slack_user_id)
        if not slack_conn:
            print("\n❌ Cannot proceed - slack user lookup failed")
            sys.exit(1)
        
        # Step 4: Test direct message
        direct_success = await test_direct_message(token, slack_user_id, args.test_message)
        
        # Step 5: Test notification flow
        notification_success = await test_notification_flow(args.user_id)
        
        # Step 6: Test send_message_to_user
        send_user_success = await debug_send_message_to_user(slack_user_id, args.test_message)
        
        # Summary
        print("\n" + "="*70)
        print("DEBUG SUMMARY")
        print("="*70)
        print(f"User Connection: ✅")
        print(f"Token Validity: {'✅' if token else '❌'}")
        print(f"Direct Message: {'✅' if direct_success else '❌'}")
        print(f"Notification Flow: {'✅' if notification_success else '❌'}")
        print(f"send_message_to_user: {'✅' if send_user_success else '❌'}")
        print("="*70)
        
        if not direct_success and not notification_success and not send_user_success:
            print("\n⚠️  All methods failed. Possible issues:")
            print("   1. Token is invalid or expired")
            print("   2. Bot doesn't have permission to message the user")
            print("   3. User has blocked the bot")
            print("   4. Slack API error")
            print("\nCheck the error messages above for details.")
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        await postgresql.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
