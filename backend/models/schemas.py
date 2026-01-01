from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    booking_details: Optional[Dict[str, Any]] = None
    action_performed: Optional[str] = None
