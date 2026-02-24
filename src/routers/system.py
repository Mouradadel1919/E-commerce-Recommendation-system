from models import ProductModel, ALSModel
from models import ResponseSignal
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

model = SentenceTransformer("intfloat/multilingual-e5-large")
logger = logging.getLogger("uvicorn.error")
app_router_sys = APIRouter()


embedding_dim = 1024
BATCH_SIZE = 200

@app_router_sys.get("/init_vectordb")
async def upload_products(request: Request):

    product_model = ProductModel(request.app.db_client)
    records = await product_model.get_all_products()
    contents = ["passage: " + p["content"] for p in records]  # extract content


    product_embeddings = model.encode(
        contents,  # use list comprehension
        batch_size=32,  # smaller batches fit in RAM
        show_progress_bar=True,
        normalize_embeddings=True 
    )

    collections = request.app.qdrant_client.get_collections().collections
    collection_names = [c.name for c in collections]

    if "products" not in collection_names:
        request.app.qdrant_client.create_collection(
            collection_name="products",
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
    query_embedding = model.encode(
        "query: " + content,
        normalize_embeddings=True,
    )

    # 3️⃣ Search in Qdrant
    search_result = request.app.qdrant_client.query_points(  # ✅ was search_points
        collection_name="products",
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



'''
@app_router_sys.get("/collaborative")
async def collaborative(request: Request):
    als_model = ALSModel(request.app.db_client)
    records = await als_model.get_user_item_score_matrix()

    return JSONResponse(
            
            content={
            "status": ResponseSignal.EVENT_FOUND_SUCCESS.value,
            "records": records
            }
        )
'''

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