from pydantic import BaseModel
from typing import Optional

class SlackEvent(BaseModel):
    type: str
    text: Optional[str] = None
    channel: Optional[str] = None
    user: Optional[str] = None
    bot_id: Optional[str] = None
    channel_type: Optional[str] = None
    subtype: Optional[str] = None

class SlackEventWrapper(BaseModel):
    type: str
    challenge: Optional[str] = None
    event: Optional[SlackEvent] = None
    token: Optional[str] = None  # Slack also sends a token field
    team_id: Optional[str] = None
