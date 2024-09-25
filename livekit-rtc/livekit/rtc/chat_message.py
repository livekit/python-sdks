from dataclasses import dataclass
from typing import Optional


@dataclass
class ChatMessage:
    id: str
    message: str
    timestamp: int
    edit_timestamp: Optional[int] = None
    generated: Optional[bool] = False
