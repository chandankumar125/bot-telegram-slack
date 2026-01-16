from pydantic import BaseModel
from typing import Literal

class BotNotification(BaseModel):
    alert_id: str
    platform: Literal["slack", "telegram"]
    channel_id: str  # For Slack: channel ID, For Telegram: chat ID
    title: str
    summary: str
