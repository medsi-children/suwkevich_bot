from fastapi import APIRouter

from app.api.v1 import messages, telegram, users

api_router = APIRouter()
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(telegram.router, prefix="/telegram", tags=["telegram"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

