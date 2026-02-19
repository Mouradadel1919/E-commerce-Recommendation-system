from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from bson.objectid import ObjectId 


class Product(BaseModel):
    mongo_id: Optional[ObjectId] = Field(None, alias="_id")
    vecdb_id: str = Field(...)
    content: str = Field(..., description="Text for RAG, e.g., product name or description")
    metadata: Dict[str, Any] = Field(..., description="All other info as metadata")

    class Config:
        arbitrary_types_allowed = True
