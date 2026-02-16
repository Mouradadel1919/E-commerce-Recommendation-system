from models import BaseDataModel
from models import Event
from models import MongoDBEnum
from models import ResponseSignal
from pymongo import InsertOne
from typing import Optional, Dict, Any, List
from uuid import uuid4  # For generating unique session IDs

class EventModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[MongoDBEnum.COLLECTION_EVENT_NAME.value]

    async def insert_many_events(self, events: list[dict]):

        docs = []

        for p in events:
            user_id = p["user_id"]
            session_id = str(uuid4())
            for e in p["events"]:
                validated = Event(
                    session_id=session_id,
                    user_id=user_id,
                    event=e  # e is already a dict
                )
                docs.append(validated.dict(by_alias=True, exclude_unset=True))
        
        result = await self.collection.insert_many(docs)
        return len(result.inserted_ids)
    
    async def get_event(self, user_id: str):
        record = await self.collection.find({
            "user_id": user_id
        })

        if record is None:
            return ResponseSignal.EVENT_FOUND_FAIL.value
        return ResponseSignal.EVENT_FOUND_SUCCESS.value
'''
    async def insert_event(self, event: list[dict]):
        event_validated = Event(**event)
        result = await self.collection.insert_one(event_validated.dict(by_alias=True, exclude_unset=True))
        event_validated.mongo_id = result.inserted_id

        return event_validated
'''  
    