from fastapi import APIRouter, Request, HTTPException, Header, BackgroundTasks
from fastapi.responses import RedirectResponse
from schemas.slack import SlackEventWrapper
from services.slack_service import handle_event
from config import SLACK_SIGNING_SECRET, SLACK_CLIENT_ID, SLACK_CLIENT_SECRET, SLACK_REDIRECT_URI
from utilis.security import verify_slack_signature
import time
import json
import requests
import uuid

router = APIRouter()

# --- OAuth Flow for "Atlassian-like" Connection ---

@router.get("/install")
def install_bot(user_id: str = "unknown"):
    """ 
    Initiates the Slack OAuth flow.
    Frontend 'Connect' button should link here: /bot/slack/install?user_id=123
    """
    if not SLACK_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Slack Client ID not configured")
    
    # Scopes needed for the bot
    scopes = "app_mentions:read,chat:write,commands,im:history,users:read"
    
    # Basic state to track user across redirect (Simple implementation)
    state = f"{user_id}:{uuid.uuid4().hex[:8]}"
    
    auth_url = (
        f"https://slack.com/oauth/v2/authorize"
        f"?client_id={SLACK_CLIENT_ID}"
        f"&scope={scopes}"
        f"&redirect_uri={SLACK_REDIRECT_URI}"
        f"&state={state}"
    )
    return RedirectResponse(auth_url)

@router.get("/oauth_callback")
async def oauth_callback(code: str, state: str = None):
    """
    Handles the callback from Slack after user authorizes the app.
    Exchanges code for access token.
    """
    if not code:
        raise HTTPException(status_code=400, detail="Missing code parameter")

    # Exchange code for token
    response = await requests.post(
        "https://slack.com/api/oauth.v2.access",
        data={
            "client_id": SLACK_CLIENT_ID,
            "client_secret": SLACK_CLIENT_SECRET,
            "code": code,
            "redirect_uri": SLACK_REDIRECT_URI
        }
    )
    
    data = response.json()
    
    if not data.get("ok"):
        raise HTTPException(status_code=400, detail=f"OAuth failed: {data.get('error')}")

    # Success! 
    # In a real app, you would now:
    # 1. Parse 'state' to get the Vibelets 'user_id'
    # 2. Store the 'access_token', 'team_id', and 'bot_user_id' in your database linked to that user.
    
    # For now, we redirect back to the dashboard with a success flag
    vibelets_user_id = state.split(":")[0] if state else "unknown"
    
    return RedirectResponse(
        f"https://preprod.vibelets.ai/dashboard/settings/integrations?status=success&platform=slack&uid={vibelets_user_id}"
    )

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
        
        if not verify_slack_signature(SLACK_SIGNING_SECRET, body_str, x_slack_request_timestamp, x_slack_signature):
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

