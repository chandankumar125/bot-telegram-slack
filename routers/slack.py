from fastapi import APIRouter, Request, HTTPException, Header, BackgroundTasks, Depends
from fastapi.responses import RedirectResponse
from schemas.slack import SlackEventWrapper
from services.slack_service import handle_event
from config import SLACK_CLIENT_ID, SLACK_REDIRECT_URI, SLACK_SIGNING_SECRET, SLACK_CLIENT_SECRET, DASHBOARD_URL
from utils.auth import get_current_user

from helpers.slack_api import verify_slack_request, authorize_slack_user, get_slack_user_info, publish_slack_message
from utils.postgres_db import save_slack_connection, get_slack_connection, disconnect_slack_connection, get_team_token
import time
import json
import requests
import uuid

router = APIRouter()

"""
1. GET /install
Initiates the OAuth flow to install the bot (Redirects user to Slack).
2. GET /oauth_callback
Handles the callback from Slack, exchanging the code for a token and saving the connection.
3. POST /disconnect
Disconnects a user by removing their connection from the database.
4. GET /status
Checks if a specific Vibelets user is currently connected to Slack.
5. POST /events
The main webhook endpoint that receives all real-time events from Slack (messages, mentions, etc.).
6. GET /events
A simple health check endpoint just to say "OK".
"""
# --- OAuth Flow for "Atlassian-like" Connection ---

@router.get("/install")
def install_bot(user_id: str = "unknown"):
    """ 
    Initiates the Slack OAuth flow.
    Frontend 'Connect' button should link here: /bot/slack/install?user_id=1
    """
    if not SLACK_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Slack Client ID not configured")
    
    # Scopes needed for the bot
    scopes = "app_mentions:read,chat:write,commands,im:history,users:read,users:read.email"
    
    # Basic state to track user across redirect (Simple implementation)
    state = f"{user_id}:{uuid.uuid4().hex[:8]}"
    
    auth_url = (
        f"https://slack.com/oauth/v2/authorize"
        f"?client_id={SLACK_CLIENT_ID}"
        f"&scope={scopes}"
        f"&redirect_uri={SLACK_REDIRECT_URI}"
        f"&state={state}"
    )
    print("\n" + "="*50)
    print(f"STAGE 1: Redirecting User to Slack Auth")
    print("-" * 50)
    print(json.dumps({
        "Client ID": SLACK_CLIENT_ID,
        "Scopes": scopes.split(","),
        "State": state
    }, indent=2))
    print("="*50 + "\n")
    return RedirectResponse(auth_url)

@router.get("/oauth_callback")
def oauth_callback(code: str, state: str = None):
    """
    Handles the callback from Slack after user authorizes the app.
    Exchanges code for access token and saves to DB.
    """
    if not code:
        raise HTTPException(status_code=400, detail="Missing code parameter")

    print("\n" + "="*50)
    print(f"STAGE 2: Received Callback from Slack")
    print("-" * 50)
    print(json.dumps({
        "Code": f"{code[:10]}...",
        "State": state
    }, indent=2))
    print("="*50 + "\n")
    
    # Exchange code for token
    from helpers.slack_api import authorize_slack_user
    try:
        # Helper uses env vars if client_id/secret are not passed
        data = authorize_slack_user(code, SLACK_REDIRECT_URI) 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to communicate with Slack: {str(e)}")
    
    if not data.get("ok"):
        raise HTTPException(status_code=400, detail=f"OAuth failed: {data.get('error')}")

    # Extract info
    access_token = data.get("access_token")
    team = data.get("team", {})
    team_id = team.get("id")
    team_name = team.get("name")
    bot_user_id = data.get("bot_user_id")
    
    # Extract Token Rotation Info
    expires_in = data.get("expires_in")
    refresh_token = data.get("refresh_token")
    
    # Extract User ID of the installing user
    authed_user = data.get("authed_user", {})
    slack_user_id = authed_user.get("id")
    
    # Parse state to get user_id
    vibelets_user_id_str = state.split(":")[0] if state else "unknown"
    
    try:
        vibelets_user_id = int(vibelets_user_id_str)
    except ValueError:
        print(f"Warning: Non-numeric user_id '{vibelets_user_id_str}' detected. Using ID 1 for testing purposes.")
        vibelets_user_id = 1

    # Fetch User Email
    email = None
    if slack_user_id:
        try:
            user_info = get_slack_user_info(access_token, slack_user_id)
            if user_info.get("ok"):
                email = user_info["user"]["profile"].get("email")
        except Exception as e:
            print(f"Failed to fetch user email: {e}")

    # Save to "Database"
    save_slack_connection(
        vibelets_user_id, team_id, team_name, access_token, bot_user_id, slack_user_id,
        refresh_token=refresh_token, expires_in=expires_in, email=email
    )
    
    # Send Welcome Message to the User
    if slack_user_id:
        try:
            welcome_msg = (
                f"👋 *Hello! I'm the Vibelets Bot.*\n"
                f"✅ **You are now successfully connected!**\n"
                f"I can help you with insights about your ad campaigns.\n\n"
                f"• Ask me questions like _'How is my campaign performing?'_\n"
            )
            publish_slack_message(access_token, slack_user_id, welcome_msg)
        except Exception as e:
            print(f"Failed to send welcome message: {e}")
    
    return RedirectResponse(
        f"{DASHBOARD_URL}?status=success&platform=slack&uid={vibelets_user_id}&team={team_name}"
    )

@router.post("/disconnect")
def disconnect_bot(user_id: str = Depends(get_current_user)):
    """
    Disconnects the user from Slack by removing their connection details.
    """
    # 1. Get connection info BEFORE disconnecting (to send goodbye msg)
    connection = get_slack_connection(user_id)
    if connection and connection.get("connected"):
        try:
            team_id = connection.get("team_id")
            slack_user_id = connection.get("slack_user_id")
            
            # Get token to send message
            token = get_team_token(team_id)
            
            if token and slack_user_id:
                goodbye_msg = (
                    f"⚠️ *You have been disconnected.*\n"
                    f"👉 <{DASHBOARD_URL}|Click here to Connect>"
                )
                publish_slack_message(token, slack_user_id, goodbye_msg)
        except Exception as e:
            print(f"Failed to send goodbye message: {e}")

    # 2. Perform Disconnect
    success = disconnect_slack_connection(user_id)
    if success:
        return {"ok": True, "message": "Disconnected successfully"}
    return {"ok": False, "message": "User not connected or user not found"}

@router.get("/status")
def get_connection_status(user_id: str = Depends(get_current_user)):
    """
    Checks if the user is connected to Slack.
    """
    connection = get_slack_connection(user_id)
    if connection and connection.get("connected"):
        # Token is stored at Team level
        token = get_team_token(connection.get("team_id"))
        return {
            "connected": True, 
            "team_name": connection.get("team_name"),
            "team_id": connection.get("team_id"),
            "slack_user_id": connection.get("slack_user_id"),
            "email": connection.get("email"),
            "bot_user_id": connection.get("bot_user_id"),
            "access_token": token
        }
    return {"connected": False}

# --- Event Handling ---

@router.post("/events")
async def slack_events(
    request: Request,
    background_tasks: BackgroundTasks,
    x_slack_signature: str = Header(None, alias="X-Slack-Signature"),
    x_slack_request_timestamp: str = Header(None, alias="X-Slack-Request-Timestamp")
):
    # Get raw body for signature verification
    body_bytes = await request.body()
    body_str = body_bytes.decode('utf-8')
    
    # Parse payload
    try:
        payload_data = json.loads(body_str)
        payload = SlackEventWrapper(**payload_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")
    
    # Verify signature for security (skip for url_verification)
    if payload.type != "url_verification" and SLACK_SIGNING_SECRET:
        if not x_slack_signature or not x_slack_request_timestamp:
            raise HTTPException(status_code=401, detail="Missing Slack signature headers")
        
        # Check timestamp to prevent replay attacks (within 5 minutes)
        try:
            current_time = int(time.time())
            request_time = int(x_slack_request_timestamp)
        except (ValueError, TypeError):
            raise HTTPException(status_code=401, detail="Invalid timestamp")
        
        if abs(current_time - request_time) > 300:
            raise HTTPException(status_code=401, detail="Request timestamp too old")
        
        if not verify_slack_request(body_str, x_slack_request_timestamp, x_slack_signature, SLACK_SIGNING_SECRET):
            raise HTTPException(status_code=401, detail="Invalid Slack signature")
    
    
    # Handle URL verification immediately
    if payload.type == "url_verification":
        return handle_event(payload)

    # Process other events in background to prevent Slack timeout
    background_tasks.add_task(handle_event, payload)
    return {"ok": True}

@router.get("/events")
def slack_events_info():
    return {"ok": True}

