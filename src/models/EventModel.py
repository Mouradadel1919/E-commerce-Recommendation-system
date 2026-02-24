from models import BaseDataModel
from models import Event
from models import MongoDBEnum
from models import ResponseSignal
from uuid import uuid4  # For generating unique session IDs



class EventModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[MongoDBEnum.COLLECTION_EVENT_NAME.value]

    async def insert_many_events(self, events: list[dict]):

        docs = []

        for p in events:
            session_id = str(uuid4())
            for e in p["events"]:
                validated = Event(
                    session_id=session_id,
                    event=e  # e is already a dict
                )
                docs.append(validated.dict(by_alias=True, exclude_unset=True))
        
        result = await self.collection.insert_many(docs)
        return len(result.inserted_ids)
    
    
    