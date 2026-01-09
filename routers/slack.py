from fastapi import APIRouter
from schemas.slack import SlackEventWrapper
from services.slack_service import handle_event

router = APIRouter()

@router.post("/events")
def slack_events(payload: SlackEventWrapper):
    return handle_event(payload)

@router.get("/events")
def slack_events_info():
    return {"ok": True}

