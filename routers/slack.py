from fastapi import APIRouter, Request, HTTPException, Header
from schemas.slack import SlackEventWrapper
from services.slack_service import handle_event
from config import SLACK_SIGNING_SECRET
from utilis.security import verify_slack_signature
import time
import json

router = APIRouter()

@router.post("/events")
async def slack_events(
    request: Request,
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
    
    return handle_event(payload)

@router.get("/events")
def slack_events_info():
    return {"ok": True}

