from models import BaseDataModel
from models import Product
from models import MongoDBEnum
from models import ResponseSignal
from fastapi import Request
from qdrant_client.models import Distance, VectorParams

import pandas as pd
import uuid

class ProductModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[MongoDBEnum.COLLECTION_PRODUCT_NAME.value]

    
    async def insert_many_products(self, prodoucts: list[dict]):

        docs = []

        for p in prodoucts:
            validated = Product(
                vecdb_id = str(uuid.uuid4()),
                content = p["content"],
                metadata = p["metadata"]
            )
            docs.append(validated.dict(by_alias=True, exclude_unset=True))
        
        result = await self.collection.insert_many(docs)
        return len(result.inserted_ids)

    
    async def get_all_products(self):
        cursor = self.collection.find({})
        records = await cursor.to_list(length=None)

        for p in records:
            p["_id"] = str(p["_id"])

        if records is None:
            return ResponseSignal.PRODUCT_FOUND_FAIL.value   
         
        return records
    