from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import SLACK_BOT_TOKEN, DASHBOARD_URL
from services.vibelets_service import resolve_query
from utils.db import get_team_token, get_vibelets_user_by_slack_id
import logging


# Configure logging
logger = logging.getLogger(__name__)

# Default client for main workspace (fallback)
default_client = WebClient(token=SLACK_BOT_TOKEN)

def get_client_for_team(team_id: str):
    token = get_team_token(team_id)
    if token:
        logger.info(f"Using team-specific token for team {team_id}")
        return WebClient(token=token)
    
    # If no token found in DB, it means the team is NOT connected (or disconnected).
    logger.warning(f"No token found for team {team_id}. Ignoring event.")
    return None

def handle_event(payload):
    """
    Handle incoming Slack events (Event Subscriptions).
    Supports: url_verification, app_mention, message.im
    """
    if payload.type == "url_verification":
        return {"challenge": payload.challenge}
    
    event = payload.event
    if not event:
        return {"ok": True}
        
    # Extract event details
    team_id = payload.team_id
    event = payload.event
    event_type = event.type
    text = event.text or ""
    user_id = getattr(event, "user", event.channel)
    channel_id = event.channel
    
    # Get the correct client for this team
    client = get_client_for_team(team_id)
    if not client:
        return {"ok": True}  # Silently ignore if disconnected from Team level (should not happen now with new logic)

    # 1. Ignore bot messages / self-events
    if hasattr(event, "bot_id") and event.bot_id:
        return {"ok": True}
    
    if event.subtype:
        return {"ok": True}

    # 2. Determine if we should reply
    should_reply = False
    if event_type == "app_mention":
        should_reply = True
    elif event_type == "message" and event.channel_type == "im":
        should_reply = True
            
    if not should_reply:
        return {"ok": True}

    # 3. Check if User is Connected
    vibelets_user_id = get_vibelets_user_by_slack_id(user_id)
    
    if not vibelets_user_id:
        # User is NOT connected (or was disconnected)
        msg = (
            f"⚠️ *Account Not Connected*\n"
            f"You need to link your Vibelets account to use this bot.\n"
            f"👉 <{DASHBOARD_URL}|Click here to Connect>"
        )
        send_message(client, channel_id, msg)
        return {"ok": True}

    # 4. Process the Message
    logger.info(f"Processing Slack event from user {user_id} (Vibelets: {vibelets_user_id}) in {channel_id}: {text}")

    # Handle Special Commands
    if text.lower().strip() == "connect":
        msg = (
            f"🔗 *Connect your Vibelets Account*\n"
            f"Please visit the Vibelets Dashboard to link your Slack account:\n"
            f"https://www.vibelets.ai/dashboard/settings/integrations?slack_id={user_id}"
        )
        send_message(client, channel_id, msg)
        return {"ok": True}

    if text.lower().strip() in ["hi", "hello", "help", "start"]:
         msg = (
            f"👋 *Hello! I'm the Vibelets Bot.*\n"
            f"I can help you with insights about your ad campaigns.\n\n"
            f"• Ask me questions like _'How is my campaign performing?'_\n"
            f"• Type *connect* to link your account.\n"
         )
         send_message(client, channel_id, msg)
         return {"ok": True}

    # 4. Resolve Query via AI
    reply = resolve_query(user_id, text)
    send_message(client, channel_id, reply)
    
    return {"ok": True}


def send_message(client: WebClient, channel_id: str, text: str):
    try:
        client.chat_postMessage(channel=channel_id, text=text)
        return {"ok": True, "status": "sent"}
    except SlackApiError as e:
        logger.error(f"Slack API Error: {str(e)}")
        return {"ok": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected Error sending Slack message: {str(e)}")
        return {"ok": False, "error": str(e)}
