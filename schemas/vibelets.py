from pydantic import BaseModel
from typing import Literal

class BotNotification(BaseModel):
    alert_id: str
    platform: Literal["telegram", "slack"]
    channel_id: str
    title: str
    summary: str
