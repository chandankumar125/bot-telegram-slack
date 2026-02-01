from pydantic import BaseModel
from typing import Literal

class BotNotification(BaseModel):
    alert_id: str
    platform: Literal["slack", "telegram", "whatsapp", "all"] = "all"
    user_id: str = None # Internal User ID (e.g. VL_TEST_USER_001)
    channel_id: str = None # Optional override (for direct targeting)
    title: str
    summary: str
