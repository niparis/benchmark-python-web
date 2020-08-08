from fastapi import APIRouter

from app.api.endpoints import routes_users

api_router = APIRouter()
api_router.include_router(routes_users.router, prefix="/users", tags=["users"])
