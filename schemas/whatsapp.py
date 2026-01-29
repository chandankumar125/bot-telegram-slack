from pydantic import BaseModel, Field
from typing import List, Optional

# --- Inner Models for Nested Structure ---

class WhatsAppText(BaseModel):
    body: str

class WhatsAppProfile(BaseModel):
    name: Optional[str] = None

class WhatsAppContact(BaseModel):
    profile: Optional[WhatsAppProfile] = None
    wa_id: Optional[str] = None

class WhatsAppMessage(BaseModel):
    from_: str = Field(..., alias="from")  # "from" is a reserved keyword in Python
    id: str
    timestamp: str
    type: str
    text: Optional[WhatsAppText] = None

class WhatsAppValue(BaseModel):
    messaging_product: str
    metadata: dict
    contacts: Optional[List[WhatsAppContact]] = []
    messages: Optional[List[WhatsAppMessage]] = []

class WhatsAppChange(BaseModel):
    value: WhatsAppValue
    field: str

class WhatsAppEntry(BaseModel):
    id: str
    changes: List[WhatsAppChange]

# --- Main Wrapper ---
class WhatsAppWebhookPayload(BaseModel):
    object: str
    entry: List[WhatsAppEntry]
