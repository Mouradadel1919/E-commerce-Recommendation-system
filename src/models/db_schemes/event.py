from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from bson.objectid import ObjectId 

class Event(BaseModel):
    mongo_id: Optional[ObjectId] = Field(None, alias="_id")
    session_id: Optional[str]= Field(None)
    event: Dict[str, Any] = Field(...)

    class Config:
        arbitrary_types_allowed = True

