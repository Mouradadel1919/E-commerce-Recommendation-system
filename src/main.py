from fastapi import FastAPI
from routers import base_router, app_router_data, app_router_sys
from helpers import get_setting
from motor.motor_asyncio import AsyncIOMotorClient
from qdrant_client import QdrantClient


app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    settings = get_setting()

    # MongoDB
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

    # Qdrant
    app.qdrant_client = QdrantClient(
        host="localhost",
        port = settings.VECTOR_DB_PORT
    )


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongo_conn.close()


app.include_router(app_router_sys)