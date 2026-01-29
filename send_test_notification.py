import sys
import os

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.slack_service import send_notification
from utils.db import get_slack_connection

def test_alert():
    user_id = "VL_TEST_USER"
    
    print(f"Fetching connection details for {user_id}...")
    connection = get_slack_connection(user_id)
    
    if not connection or not connection.get("connected"):
        print("❌ User is not connected to Slack.")
        return

    team_id = connection.get("team_id")
    slack_user_id = connection.get("slack_user_id")
    
    print(f"✅ Found Connection: Team {team_id}, User {slack_user_id}")
    print("🚀 Sending test alert...")
    
    result = send_notification(
        team_id=team_id,
        channel_id=slack_user_id,
        text="🚀 *Test Alert*: If you see this, the notification system is working perfectly!"
    )
    
    print(f"Result: {result}")

if __name__ == "__main__":
    test_alert()
