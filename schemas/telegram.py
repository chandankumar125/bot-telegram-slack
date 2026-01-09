from pydantic import BaseModel
from typing import Optional

class TelegramChat(BaseModel):
    id: int
    type: str

class TelegramMessage(BaseModel):
    chat: TelegramChat
    text: Optional[str]

class TelegramWebhook(BaseModel):
    message: Optional[TelegramMessage]
