from models import ProductModel, ALSModel
from models import ResponseSignal
from models import MongoDBEnum, VectorDBEnum
from helpers import get_setting
import logging
import os
from models import ResponseSignal

from fastapi.responses import JSONResponse
from fastapi import APIRouter, Request
from sentence_transformers import SentenceTransformer
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct


settings = get_setting()
os.environ["HF_TOKEN"] = settings.HF_TOKE
logger = logging.getLogger("uvicorn.error")

embedding_dim = 1024
BATCH_SIZE = 200

model = SentenceTransformer(settings.SENTENCE_TRANSFORMER)

app_router_sys = APIRouter()

@app_router_sys.get("/init_vectordb")
async def upload_products(request: Request):

    product_model = ProductModel(request.app.db_client)
    records = await product_model.get_all_products()
    contents = ["passage: " + p["content"] for p in records]


    product_embeddings = model.encode(
        contents,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True 
    )

    collections = request.app.qdrant_client.get_collections().collections
    collection_names = [c.name for c in collections]

    if VectorDBEnum.COLLECTION_PRODUCTS_NAME.value not in collection_names:
        request.app.qdrant_client.create_collection(
            collection_name=VectorDBEnum.COLLECTION_PRODUCTS_NAME.value,
            vectors_config=VectorParams(
                size=embedding_dim,
                distance=Distance.COSINE
            )
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
            collection_name=VectorDBEnum.COLLECTION_PRODUCTS_NAME.value,
            points=batch
        )

@app_router_sys.get("/content/{vecdb_id}")
async def test_retrieval(request: Request, vecdb_id: str):

    # 1️⃣ Get product from Mongo
    product = await request.app.db_client[MongoDBEnum.COLLECTION_PRODUCT_NAME.value].find_one(
        {"vecdb_id": str(vecdb_id)}
    )

    if not product:
        return {"error": ResponseSignal.PRODUCT_FOUND_FAIL.value}

    content = product["content"]

    # 2️⃣ Encode query
    query_embedding = model.encode(
        "query: " + content,
        normalize_embeddings=True,
    )

    # 3️⃣ Search in Qdrant
    search_result = request.app.qdrant_client.query_points(  # ✅ was search_points
        collection_name=VectorDBEnum.COLLECTION_PRODUCTS_NAME.value,
        query=query_embedding.tolist(),
        limit=6
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
        "results": results[1:]
    }


@app_router_sys.get("/collaborative/{user_id}")
async def collaborative(request: Request, user_id: str, n: int = 10):
    als_model = ALSModel(request.app.db_client)
    records = await als_model.get_user_item_score_matrix()

    sparse_matrix = als_model.build_sparse_matrix(records)
    als_model.train(sparse_matrix)
    recommendations = als_model.recommend(user_id, sparse_matrix, n)

    return JSONResponse(content={
        "status": ResponseSignal.EVENT_FOUND_SUCCESS.value,
        "user_id": user_id,
        "recommendations": recommendations
    })


@app_router_sys.get("/final/{user_id}")
async def collaborative(request: Request, user_id: str, n: int = 10):
    
    # 1️⃣ Get user interactions from event collection
    events = await request.app.db_client[MongoDBEnum.COLLECTION_EVENT_NAME.value].find(
        {"event.user_id": user_id},
        {"event.product_link": 1}
    ).to_list(length=None)

    product_links = list({
        e["event"]["product_link"] for e in events if "event" in e and "product_link" in e["event"]
    })

    # 2️⃣ Content-based: iterate each product link
    content_based_results = []

    for product_link in product_links:   

        product = await request.app.db_client[MongoDBEnum.COLLECTION_PRODUCT_NAME.value].find_one(
            {"metadata.product_link" : product_link}
        )

        if not product:
            continue

        content = product["content"]

        query_embedding = model.encode(
            "query: " + content,
            normalize_embeddings=True,
        )

        search_result = request.app.qdrant_client.query_points(
            collection_name=VectorDBEnum.COLLECTION_PRODUCTS_NAME.value,
            query=query_embedding.tolist(),
            limit=6
        )

        for hit in search_result.points:
            content_based_results.append({
                "score": hit.score,
                "content": hit.payload.get("content"),
                "metadata": hit.payload.get("metadata")
            })

    # Sort by score and take top 3
    top_content_based = sorted(content_based_results, key=lambda x: x["score"], reverse=True)[1:]

    # 3️⃣ Collaborative filtering (ALS)
    als_model = ALSModel(request.app.db_client)
    records = await als_model.get_user_item_score_matrix()

    sparse_matrix = als_model.build_sparse_matrix(records)
    als_model.train(sparse_matrix)
    als_recommendations = als_model.recommend(user_id, sparse_matrix, n)

    # 4️⃣ Return combined results
    return {
        "user_id": user_id,
        "content_based": top_content_based,
        "collaborative": als_recommendations
    }
