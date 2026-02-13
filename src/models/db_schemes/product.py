from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from bson.objectid import ObjectId 


class Product(BaseModel):
    mongo_id: Optional[ObjectId] = Field(None, alias="_id")
    content: str = Field(..., description="Text for RAG, e.g., product name or description")
    metadata: Dict[str, Any] = Field(..., description="All other info as metadata")

    class Config:
        arbitrary_types_allowed = True


    '''
    id_: Optional[ObjectId]= Field(None)
    name: str= Field(...)
    product_id: str= Field(...)
    category: str= Field(...)
    stock: str= Field()
    price: float= Field(...)
    product_link: str= Field(...)
    '''