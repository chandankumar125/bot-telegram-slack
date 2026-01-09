from pydantic import BaseModel
from typing import Optional, Dict, Any

class BotQueryRequest(BaseModel):
    user_id: str
    question: str
    alert_id: Optional[str]

class BotQueryResponse(BaseModel):
    answer: str
    metadata: Optional[Dict[str, Any]]
