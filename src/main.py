from fastapi import FastAPI
from routers import base_router, app_router_data, app_router_sys
from helpers import get_setting
from motor.motor_asyncio import AsyncIOMotorClient
from qdrant_client import QdrantClient
from models import ProductModel
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

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

    # Create collection if not exists
    embedding_dim = 768  # mpnet model dimension

    collections = app.qdrant_client.get_collections().collections
    collection_names = [c.name for c in collections]

    if "products" not in collection_names:
        app.qdrant_client.create_collection(
            collection_name="products",
            vectors_config=VectorParams(
                size=embedding_dim,
                distance=Distance.COSINE
            )
        )

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongo_conn.close()


app.include_router(app_router_sys)