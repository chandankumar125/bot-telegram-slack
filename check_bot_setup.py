"""
Check if your bot is properly configured and get the exact bot name
"""
import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from config import SLACK_BOT_TOKEN

print("="*60)
print("Bot Setup Checker")
print("="*60)
print()

if not SLACK_BOT_TOKEN:
    print("ERROR: SLACK_BOT_TOKEN is not set!")
    print()
    print("Please set it in your .env file:")
    print("   SLACK_BOT_TOKEN=xoxb-your-token-here")
    print()
    print("To get your token:")
    print("   1. Go to: https://api.slack.com/apps/A0A90BVE0PJ/oauth")
    print("   2. Find 'Bot User OAuth Token'")
    print("   3. Copy it to your .env file")
    exit(1)

print(f"✓ SLACK_BOT_TOKEN is set")
print()

try:
    client = WebClient(token=SLACK_BOT_TOKEN)
    response = client.auth_test()
    
    print("="*60)
    print("SUCCESS: Bot is properly configured!")
    print("="*60)
    print()
    print(f"Bot Name:     {response['user']}")
    print(f"Bot ID:       {response['user_id']}")
    print(f"Workspace:    {response['team']}")
    print(f"Team ID:      {response['team_id']}")
    print()
    print("="*60)
    print("To invite this bot to a channel, use:")
    print("="*60)
    print(f"   /invite @{response['user']}")
    print()
    print("Or try:")
    print(f"   /invite {response['user']}")
    print()
    print("Alternative method:")
    print("   1. Click channel name → Integrations → Add apps")
    print(f"   2. Search for '{response['user']}'")
    print("   3. Click Add")
    print()
    
except Exception as e:
    print("="*60)
    print("ERROR: Cannot connect to Slack")
    print("="*60)
    print()
    print(f"Error: {str(e)}")
    print()
    print("Possible issues:")
    print("   1. SLACK_BOT_TOKEN is incorrect")
    print("   2. Bot is not installed to workspace")
    print("   3. Token has been revoked")
    print()
    print("To fix:")
    print("   1. Go to: https://api.slack.com/apps/A0A90BVE0PJ/oauth")
    print("   2. Click 'Install to Workspace' if not installed")
    print("   3. Copy the 'Bot User OAuth Token'")
    print("   4. Update your .env file")
    print()
