from pydantic import BaseModel
from typing import Optional

class Event(BaseModel):
    user_id: str
    event_type: str
    product_link: str
    duration: Optional[float] = None  # optional, for product_exit
    timestamp: Optional[str] = None
