from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.api.servicesfac import get_user_services
from app.domain.users.users_schema import (
    UserCreateSchema,
    UserDBSchema,
    UserUpdateSchema,
)
from app.domain.users.users_service import UserService

router = APIRouter()


@router.post("/", response_model=UserDBSchema)
async def create_user(
    user: UserCreateSchema,
    user_service: UserService = Depends(get_user_services),
) -> UserDBSchema:
    return await user_service.create_user(user)


@router.get("/all", response_model=List[UserDBSchema])
async def list_users(
    user_service: UserService = Depends(get_user_services),
) -> List[UserDBSchema]:
    users: List[UserDBSchema] = await user_service.list_users()
    return users


@router.get("/{user_id}", response_model=UserDBSchema)
def get_user_by_id(
    user_id: int,
    user_service: UserService = Depends(get_user_services),
) -> Optional[UserDBSchema]:
    user = user_service.get_user_by_id(db, user_id)
    if user:
        return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User with id:{user_id} not found",
    )


@router.put("/{user_id}", response_model=UserDBSchema)
def update_user(
    user_id: int,
    new_user: UserUpdateSchema,
    user_service: UserService = Depends(get_user_services),
) -> UserDBSchema:
    user_updated: UserDBSchema = user_service.update_user(
        db, user_id, new_user
    )
    return user_updated


@router.delete("/{user_id}", response_model=UserDBSchema)
def remove_user(
    user_id: int,
    user_service: UserService = Depends(get_user_services),
) -> UserDBSchema:
    user_removed = user_service.remove_user(db, user_id)

    if user_removed:
        return user_removed
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User with id:{user_id} not found",
    )
