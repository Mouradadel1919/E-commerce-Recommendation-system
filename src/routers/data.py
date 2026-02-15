from models import ProductModel
from models import Product, ProductEnums, ResponseSignal
from helpers import get_products
import logging
from fastapi import FastAPI, APIRouter, Request




logger = logging.getLogger("uvicorn.error")
app_router_data = APIRouter()

products = get_products(path=ProductEnums.PRODUCTS_FILE_PATH.value)


@app_router_data.post("/upload")
async def upload_products(request: Request):

    if not products:
        return {"inserted": 0, "message": "No products found"}

    product_model = ProductModel(request.app.db_client)

    inserted = await product_model.insert_many_products(products)

    return {
        "status": ResponseSignal.PRODUCT_UPLOAD_SUCCESS.value,
        "inserted": inserted
    }