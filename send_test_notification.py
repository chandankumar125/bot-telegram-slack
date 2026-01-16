"""
Quick script to send a test notification to Slack

Usage:
    python send_test_notification.py <channel_id> [title] [summary]

Example:
    python send_test_notification.py C1234567890 "Test Alert" "This is a test"
"""

import requests
import sys
import time
import json

BASE_URL = "http://localhost:8000"

def send_notification(channel_id: str, title: str = None, summary: str = None):
    """Send a test notification to Slack"""
    
    if not channel_id:
        print("❌ Error: Channel ID is required")
        print("\nUsage: python send_test_notification.py <channel_id> [title] [summary]")
        print("\nTo find your channel ID:")
        print("  - Right-click channel in Slack → View channel details")
        print("  - Or use: https://api.slack.com/methods/conversations.list")
        return False
    
    payload = {
        "alert_id": f"test-{int(time.time())}",
        "platform": "slack",
        "channel_id": channel_id,
        "title": title or "🚀 Test Notification",
        "summary": summary or "This is a test notification from the Vibelets bot. Try asking a question about this alert!"
    }
    
    print(f"📤 Sending notification to channel: {channel_id}")
    print(f"   Title: {payload['title']}")
    print(f"   Summary: {payload['summary']}")
    print()
    
    try:
        response = requests.post(
            f"{BASE_URL}/bot/notify",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok") or result.get("status") == "sent":
                print("✅ Notification sent successfully!")
                print(f"\n📬 Check your Slack channel: {channel_id}")
                print("💡 Try asking a question like:")
                print("   - 'What caused this alert?'")
                print("   - 'Tell me more about this'")
                print("   - 'Why did this happen?'")
                return True
            else:
                print(f"❌ Notification failed: {json.dumps(result, indent=2)}")
                return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server")
        print("   Make sure your server is running:")
        print("   uvicorn main:app --reload --port 8000")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python send_test_notification.py <channel_id> [title] [summary]")
        print("\nExample:")
        print('  python send_test_notification.py C1234567890 "Server Alert" "CPU usage is high"')
        sys.exit(1)
    
    channel_id = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else None
    summary = sys.argv[3] if len(sys.argv) > 3 else None
    
    send_notification(channel_id, title, summary)
