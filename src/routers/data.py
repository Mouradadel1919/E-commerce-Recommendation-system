from models import ProductModel, EventModel
from models import Product, ProductEnums, ResponseSignal, EventsEnums
from helpers import get_products, get_events, user_interactions
import logging
from fastapi.responses import JSONResponse
from fastapi import FastAPI, APIRouter, Request, status




logger = logging.getLogger("uvicorn.error")
app_router_data = APIRouter()

products = get_products(path=ProductEnums.PRODUCTS_FILE_PATH.value)


@app_router_data.post("/products")
async def upload_products(request: Request):

    if not products:
        return {"inserted": 0, "message": ResponseSignal.PRODUCT_FOUND_FAIL.value}

    product_model = ProductModel(request.app.db_client)
    inserted = await product_model.insert_many_products(products)

    return JSONResponse(
            
            content={
            "status": ResponseSignal.PRODUCT_UPLOAD_SUCCESS.value,
            "inserted": inserted
            }
        )

events = get_products(path=EventsEnums.EVENTS_FILE_PATH.value)

@app_router_data.post("/events")
async def upload_events(request: Request):

    if not events:
        return {"inserted": 0, "message": ResponseSignal.EVENT_FOUND_FAIL.value}

    event_model = EventModel(request.app.db_client)
    inserted = await event_model.insert_many_events(events)

    return JSONResponse(
            
            content={
            "status": ResponseSignal.EVENT_FOUND_SUCCESS.value,
            "inserted": inserted
            }
        )

@app_router_data.get("/interactions/{user_id}")
async def user_tracking(user_id: str, request: Request):
    user_event = user_interactions(user_id=user_id, duration_sec=300)  # 5 min tracking
    
    event_model = EventModel(request.app.db_client)
    inserted = await event_model.insert_many_events(user_event)

    return JSONResponse(
            
            content={
            "status": ResponseSignal.EVENT_FOUND_SUCCESS.value,
            "inserted": inserted
            }
        )