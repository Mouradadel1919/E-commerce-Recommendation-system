from models import ProductModel, EventModel
from models import Product, ProductEnums, ResponseSignal, EventsEnums
from helpers import get_products, get_events, user_interactions, get_setting
import logging
import os
from models import ResponseSignal


from bson import ObjectId
from fastapi.responses import JSONResponse
from fastapi import FastAPI, APIRouter, Request, status
from sentence_transformers import SentenceTransformer
from pymongo import UpdateOne
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct

settings = get_setting()

os.environ["HF_TOKEN"] = settings.HF_TOKE

model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
logger = logging.getLogger("uvicorn.error")
app_router_sys = APIRouter()


embedding_dim = 768
BATCH_SIZE = 200
@app_router_sys.get("/init_vectordb")
async def upload_products(request: Request):

    product_model = ProductModel(request.app.db_client)
    records = await product_model.get_all_products()
    contents = [p["content"] for p in records]  # extract content


    product_embeddings = model.encode(
        contents,  # use list comprehension
        batch_size=64,  # smaller batches fit in RAM
        show_progress_bar=True
    )


    points = [
    PointStruct(
        id=str(p["vecdb_id"]),
        vector=emb.tolist(),
        payload={
            "content": p["content"],
            "metadata": p["metadata"]
        }
    )
    for p, emb in zip(records, product_embeddings)
    ]

    for i in range(0, len(points), BATCH_SIZE):
        batch = points[i:i+BATCH_SIZE]

        request.app.qdrant_client.upsert(
            collection_name="products",
            points=batch
        )

@app_router_sys.get("/test-retrieval/{vecdb_id}")
async def test_retrieval(request: Request, vecdb_id: str):

    # 1️⃣ Get product from Mongo
    product = await request.app.db_client["Product"].find_one(
        {"vecdb_id": str(vecdb_id)}
    )

    if not product:
        return {"error": "Product not found"}

    content = product["content"]

    # 2️⃣ Encode query
    query_embedding = model.encode(content)

    # 3️⃣ Search in Qdrant
    search_result = request.app.qdrant_client.query_points(  # ✅ was search_points
        collection_name="products",
        query=query_embedding.tolist(),
        limit=5
    )

    # 4️⃣ Format results
    results = []
    for hit in search_result.points:  # ✅ no .result needed, search() returns a list directly
        results.append({
            "score": hit.score,
            "content": hit.payload.get("content"),    # ✅ was .get["content"]
            "metadata": hit.payload.get("metadata")   # ✅ was .get["metadata"]
        })

    return {
        "query_product": content,
        "results": results
    }

    '''
    query_embedding = model.encode(user_clicked_product_content)

search_result = request.app.qdrant_client.search(
    collection_name="products",
    query_vector=query_embedding.tolist(),
    limit=5
)

recommended_products = [
    hit.payload for hit in search_result
]

    '''
    


'''
    # Update embeddings asynchronously
    bulk_ops = [
    UpdateOne(
        {"_id": ObjectId(p["_id"])},               # match by MongoDB ID
        {"$set": {"embedding": emb.tolist()}}  # add embedding field
    )
    for p, emb in zip(records, product_embeddings)
    ]

    # update all at once
    await request.app.db_client["Product"].bulk_write(bulk_ops)

    return {"message": ResponseSignal.EMBEDDING_UPLOADED_SUCCESS.value, "count": len(product_embeddings)}
'''