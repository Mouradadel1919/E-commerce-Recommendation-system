from fastapi import FastAPI, APIRouter, Depends
from helpers import Settings, get_setting

base_router = APIRouter()

@base_router.get("/")
async def welcome_page(settings: Settings= Depends(get_setting)):
    return {
        "APP_NAME": settings.APP_NAME,
        "APP_VERSION": settings.APP_VERSION
    }