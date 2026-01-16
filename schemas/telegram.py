from pydantic import BaseModel
from typing import Optional, Dict, Any

class TelegramUser(BaseModel):
    id: int
    is_bot: Optional[bool] = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None

class TelegramChat(BaseModel):
    id: int
    type: str  # "private", "group", "supergroup", "channel"
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class TelegramMessage(BaseModel):
    message_id: int
    from_: Optional[TelegramUser] = None
    chat: TelegramChat
    date: int
    text: Optional[str] = None
    caption: Optional[str] = None
    
    class Config:
        # Telegram API uses "from" which is a Python keyword
        fields = {"from_": "from"}

class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[TelegramMessage] = None
    edited_message: Optional[TelegramMessage] = None
    channel_post: Optional[TelegramMessage] = None
    
    class Config:
        # Allow extra fields that Telegram might send
        extra = "allow"
