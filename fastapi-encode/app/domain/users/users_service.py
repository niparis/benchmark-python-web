from typing import Any, List, Optional

from sqlalchemy.orm import Session

from app.domain.users.users_schema import (
    UserCreateSchema,
    UserDBSchema,
    UserUpdateSchema,
)


class UserService:
    def __init__(self, user_queries: Any):
        self.__user_queries = user_queries

    async def create_user(self, user: UserCreateSchema) -> UserDBSchema:
        new_user = await self.__user_queries.create_user(user)
        return UserDBSchema.from_orm(new_user)

    async def list_users(self) -> List[UserDBSchema]:
        users = await self.__user_queries.get_all_users()
        users_schema = [UserDBSchema(**{k:v for k,v in zip(user.keys(), user.values())}) for user in users]  #kinda not noob friendly
        return users_schema

    def get_user_by_id(
        self, db: Session, user_id: int
    ) -> Optional[UserDBSchema]:
        user = self.__user_queries.get_user_byid(db, user_id)
        if user:
            return UserDBSchema.from_orm(user)
        else:
            return None

    def update_user(
        self, db: Session, user_id: int, new_user: UserUpdateSchema
    ) -> UserDBSchema:
        old_user = self.__user_queries.get_user_byid(db, user_id)
        user_updated = self.__user_queries.update_user(db, old_user, new_user)
        return UserDBSchema.from_orm(user_updated)

    def remove_user(self, db: Session, user_id: int) -> Optional[UserDBSchema]:
        user_removed = self.__user_queries.delete_user(db, user_id)
        if user_removed:
            return UserDBSchema.from_orm(user_removed)
        else:
            return None
