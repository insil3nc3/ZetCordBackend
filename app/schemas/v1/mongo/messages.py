from typing import Optional
from pydantic import BaseModel

class PrivateMessage(BaseModel):
    chat_id: str
    sender_id: int
    content: str
    timestamp: str
    edited: bool = False
