from config import SLACK_BOT_TOKEN, DASHBOARD_URL, SLACK_CLIENT_ID, SLACK_CLIENT_SECRET
from services.vibelets_service import resolve_query
from utils.postgres_db import get_vibelets_user_by_slack_id, get_team_data, update_team_token, get_connection_by_slack_user_id
import logging
import time
from helpers.slack_api import refresh_slack_token

# Configure logging
logger = logging.getLogger(__name__)

# Default client for main workspace (fallback)
from helpers.slack_api import refresh_slack_token, publish_slack_message

# Configure logging
logger = logging.getLogger(__name__)

def ensure_valid_token(team_id: str):
    """
    Checks if token is expired and refreshes if needed.
    Returns valid access_token.
    """
    team_data = get_team_data(team_id)
    if not team_data:
        return None
    
    access_token = team_data.get("access_token")
    expires_at = team_data.get("expires_at")
    refresh_token = team_data.get("refresh_token")
    
    # If no expiry info, it's a legacy non-expiring token
    if not expires_at or not refresh_token:
        logger.info(f"Team {team_id}: No expiry found. Using existing token.")
        return access_token
    
    # Check if expired (with 5 minute buffer)
    # Ensure expires_at is a timestamp (float/int)
    if hasattr(expires_at, 'timestamp'): 
        expires_at = expires_at.timestamp()
        
    time_left = expires_at - time.time()
    logger.info(f"Team {team_id}: Token expires in {time_left:.0f} seconds.")

    if time.time() > (expires_at - 300):
        logger.info(f"Token for team {team_id} expired/expiring. Refreshing...")
        
        try:
            data = refresh_slack_token(refresh_token)
            
            if data.get("ok"):
                 new_access_token = data.get("access_token")
                 new_refresh_token = data.get("refresh_token")
                 new_expires_in = data.get("expires_in")
                 
                 update_team_token(team_id, new_access_token, new_refresh_token, new_expires_in)
                 logger.info(f"Token refreshed successfully for team {team_id}")
                 return new_access_token
            else:
                logger.error(f"Failed to refresh token: {data.get('error')}")
                # Fallback to existing token (might fail)
                return access_token
                
        except Exception as e:
            logger.error(f"Error during token refresh: {e}")
            return access_token

    return access_token

def get_token_for_team(team_id: str):
    # Use the smart token retriever
    token = ensure_valid_token(team_id)
    
    if token:
        logger.info(f"Using team-specific token for team {team_id}")
        return token
    
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
        
    # Extract event details; Extract Slack ID:
    team_id = payload.team_id
    event = payload.event
    event_type = event.type
    text = event.text or ""
    user_id = getattr(event, "user", event.channel)
    channel_id = event.channel
    
    # Get the correct token for this team
    token = get_token_for_team(team_id)
    if not token:
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
        send_message(token, channel_id, msg)
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
        send_message(token, channel_id, msg)
        return {"ok": True}

    if text.lower().strip() in ["hi", "hello", "help", "start"]:
         msg = (
            f"👋 *Hello! I'm the Vibelets Bot.*\n"
            f"I can help you with insights about your ad campaigns.\n\n"
            f"• Ask me questions like _'How is my campaign performing?'_\n"
            f"• Type *connect* to link your account.\n"
         )
         send_message(token, channel_id, msg)
         return {"ok": True}

    # 4. Resolve Query via AI
    reply = resolve_query(vibelets_user_id, text)
    send_message(token, channel_id, reply)
    
    return {"ok": True}



# --- PUBLIC METHODS FOR OUTSIDE USE ---

def send_message_to_user(slack_user_id: str, text: str):
    """
    Sends a message to a Slack user, automatically finding their team and token.
    This is designed for cross-service calls (like notifications).
    """
    # 1. Use optimized query to get team and token directly from slack_user_id
    connection = get_connection_by_slack_user_id(slack_user_id)
    
    if not connection:
        logger.error(f"Notify Error: No connection found for slack_user_id={slack_user_id}")
        return {"ok": False, "error": "User/Team not found"}
        
    team_id = connection.get("team_id")
    
    # 2. Get Client (using wrapper handles refresh if needed)
    token = get_token_for_team(team_id)
    if not token:
        logger.error(f"Notify Error: No token found for team_id={team_id}")
        return {"ok": False, "error": "Team token not found"}

    # 3. Send
    return send_message(token, slack_user_id, text)


def send_message(token: str, channel_id: str, text: str):
    try:
        # Using the helper instead of WebClient
        publish_slack_message(token, channel_id, text)
        return {"ok": True, "status": "sent"}
    except Exception as e:
        logger.error(f"Error sending Slack message: {str(e)}")
        return {"ok": False, "error": str(e)}

def send_notification(team_id: str, channel_id: str, text: str):
    """
    Sends a proactive notification to a specific team and channel/user.
    Can be called from other modules.
    """
    token = get_token_for_team(team_id)
    if token:
        return send_message(token, channel_id, text)
    return {"ok": False, "error": "Team not connected"}
