import asyncio
from fastapi import FastAPI, routing, APIRouter
from app.api.v1.routers.auth.auth import auth_router

app = FastAPI()
app.include_router(auth_router)