from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = datetime.now()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    domain: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    session_id: str
    domain: str
    timestamp: datetime = datetime.now()

class ConversationHistory(BaseModel):
    session_id: str
    domain: str
    messages: List[ChatMessage] = []
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class DomainInfo(BaseModel):
    domain_id: str
    name: str
    description: str
    is_active: bool = True
