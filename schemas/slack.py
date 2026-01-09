from pydantic import BaseModel
from typing import Optional

class SlackEvent(BaseModel):
    type: str
    text: Optional[str]
    channel: Optional[str]

class SlackEventWrapper(BaseModel):
    type: str
    challenge: Optional[str]
    event: Optional[SlackEvent]
