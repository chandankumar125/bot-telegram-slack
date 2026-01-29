
import os
from dotenv import load_dotenv

load_dotenv()

def print_box(content):
    lines = content.split('\n')
    width = max(len(line) for line in lines) + 4
    print("+" + "-" * width + "+")
    for line in lines:
        print(f"|  {line:<{width-4}}  |")
    print("+" + "-" * width + "+")

def main():
    print("\n🚀 Slack Webhook Configuration Helper 🚀\n")
    
    # 1. Get Base URL
    print("Slack does not support setting webhooks via API (unlike Telegram).")
    print("You must manually configure this in the Slack App Dashboard.\n")
    
    # Hardcoded URL for convenience
    base_url = "https://unintroducible-elocutionary-rylee.ngrok-free.dev"
    print(f"✅ Using NGROK URL: {base_url} (Forwarding to http://localhost:8000)")

    if not base_url:
        print("❌ URL is required.")
        return

    # 2. Redirect URL
    redirect_url = f"{base_url}/bot/slack/oauth_callback"
    
    # 3. Events URL
    events_url = f"{base_url}/bot/slack/events"
    
    # 4. Instructions
    print("\n" + "="*50)
    print("STEP 1: OAUTH & PERMISSIONS")
    print("="*50)
    print("Go to: https://api.slack.com/apps > Choose App > OAuth & Permissions")
    print("\n👉 Add this Redirect URL:")
    print_box(redirect_url)
    print("\n👉 Ensure these Bot Token Scopes are added:")
    print("- app_mentions:read")
    print("- chat:write")
    print("- commands")
    print("- im:history")
    print("- users:read")
    print("- users:read.email")

    print("\n" + "="*50)
    print("STEP 2: EVENT SUBSCRIPTIONS")
    print("="*50)
    print("Go to: Event Subscriptions > Enable Events 'On'")
    print("\n👉 Paste this Request URL:")
    print_box(events_url)
    print("\n(Slack will verify this URL immediately. Ensure your server is running!)")
    print("\n👉 Subscribe to these events:")
    print("- app_mention")
    print("- message.im")

    print("\n" + "="*50)
    print("STEP 3: UPDATE .ENV")
    print("="*50)
    print("Ensure SLACK_REDIRECT_URI in your .env matches the one above!")
    
    current_env = os.getenv("SLACK_REDIRECT_URI", "Not Set")
    if current_env != redirect_url:
        print(f"\n⚠️  MISMATCH FOUND!")
        print(f"Current .env: {current_env}")
        print(f"Required:     {redirect_url}")
        print("Please update your .env file.")
    else:
        print("\n✅ .env matches perfectly!")

if __name__ == "__main__":
    main()
