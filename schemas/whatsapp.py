from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class WhatsAppContact(BaseModel):
    profile: Optional[Dict[str, str]] = None
    wa_id: str  # WhatsApp ID (phone number)

class WhatsAppText(BaseModel):
    body: str

class WhatsAppMessage(BaseModel):
    from_: Optional[str] = Field(None, alias="from")  # Phone number (using alias for "from")
    id: str
    timestamp: str
    type: str  # "text", "image", "video", etc.
    text: Optional[WhatsAppText] = None
    
    class Config:
        populate_by_name = True

class WhatsAppEntry(BaseModel):
    id: str
    changes: List[Dict[str, Any]]

class WhatsAppValue(BaseModel):
    messaging_product: str
    metadata: Optional[Dict[str, Any]] = None
    contacts: Optional[List[WhatsAppContact]] = None
    messages: Optional[List[WhatsAppMessage]] = None
    statuses: Optional[List[Dict[str, Any]]] = None

class WhatsAppChange(BaseModel):
    value: WhatsAppValue
    field: str

class WhatsAppWebhook(BaseModel):
    object: str
    entry: List[WhatsAppEntry]
    
    class Config:
        extra = "allow"
