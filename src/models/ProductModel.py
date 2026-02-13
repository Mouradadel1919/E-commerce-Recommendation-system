from models import BaseDataModel
from models import Product
from models import MongoDBEnum
from models import ResponseSignal

class ProductModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[MongoDBEnum.COLLECTION_PRODUCT_NAME.value]

    
    async def insert_many_products(self, prodoucts: list[dict]):

        docs = []

        for p in prodoucts:
            validated = Product(**p)
            docs.append(validated.dict(by_alias=True, exclude_unset=True))
        
        result = await self.collection.insert_many(docs)
        return len(result.inserted_ids)

    
    async def get_product(self, product_id: str):
        record = await self.collection.find_one({
            "product_id": product_id
        })

        if record is None:
            return ResponseSignal.PRODUCT_FOUND_FAIL.value
        return ResponseSignal.PRODUCT_FOUND_SUCCESS.value