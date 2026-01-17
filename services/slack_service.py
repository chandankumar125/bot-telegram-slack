from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import SLACK_BOT_TOKEN
from services.vibelets_service import resolve_query
import logging

# Configure logging
logger = logging.getLogger(__name__)

client = WebClient(token=SLACK_BOT_TOKEN)

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
    event_type = event.type
    text = event.text or ""
    user_id = getattr(event, "user", event.channel)
    channel_id = event.channel
    
    # 1. Ignore bot messages / self-events
    if hasattr(event, "bot_id") and event.bot_id:
        return {"ok": True}
    
    if event.subtype:
        # Ignore subtypes like message_changed, message_deleted etc. for now
        return {"ok": True}

    # 2. Determine if we should reply
    should_reply = False
    
    if event_type == "app_mention":
        # Always reply when mentioned in a channel
        should_reply = True
    elif event_type == "message":
        # Reply to Direct Messages (IM)
        if event.channel_type == "im":
            should_reply = True
            
    if not should_reply:
        return {"ok": True}

    # 3. Process the Message
    logger.info(f"Processing Slack event from user {user_id} in {channel_id}: {text}")

    # Handle Special Commands
    if text.lower().strip() == "connect":
        # Send connection/auth instructions
        # PROD TODO: Generate a unique link via Vibelets API
        msg = (
            f"🔗 *Connect your Vibelets Account*\n"
            f"Please visit the Vibelets Dashboard to link your Slack account:\n"
            f"https://www.vibelets.ai/dashboard/settings/integrations?slack_id={user_id}"
        )
        send_message(channel_id, msg)
        return {"ok": True}

    if text.lower().strip() in ["hi", "hello", "help", "start"]:
         msg = (
            f"👋 *Hello! I'm the Vibelets Bot.*\n"
            f"I can help you with insights about your ad campaigns.\n\n"
            f"• Ask me questions like _'How is my campaign performing?'_\n"
            f"• Type *connect* to link your account.\n"
        )
         send_message(channel_id, msg)
         return {"ok": True}

    # 4. Resolve Query via AI
    # Send a ephemeral 'typing' or acknowledgment if possible (not supported in simple event API easily without socket mode)
    reply = resolve_query(user_id, text)
    send_message(channel_id, reply)
    
    return {"ok": True}


def send_message(channel_id: str, text: str):
    try:
        client.chat_postMessage(channel=channel_id, text=text)
        return {"ok": True, "status": "sent"}
    except SlackApiError as e:
        logger.error(f"Slack API Error: {str(e)}")
        return {"ok": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected Error sending Slack message: {str(e)}")
        return {"ok": False, "error": str(e)}
