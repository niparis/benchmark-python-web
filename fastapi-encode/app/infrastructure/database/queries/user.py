from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from app.core.db import db
from app.domain.users.users_schema import UserCreateSchema, UserUpdateSchema
from app.infrastructure.database.models.users import t_users as UserModel


class UserQueries:
    async def create_user(self, user: UserCreateSchema) -> UserModel:
        query = UserModel.insert()
        user_id = await db.execute(query=query, values=user.__dict__)
        user.__dict__.update(
            {"user_id": user_id}
        )  # note that it's not going to take in account
        return user

    # def update_user(
    #     self, db: Session, old_user: UserModel, new_user: UserUpdateSchema
    # ) -> UserModel:
    #     for key, value in new_user.dict().items():
    #         setattr(old_user, key, value)

    #     db.add(old_user)
    #     db.commit()
    #     db.refresh(old_user)
    #     return old_user

    # def delete_user(self, db: Session, user_id: int) -> Optional[UserModel]:
    #     user = self.get_user_byid(db, user_id)
    #     if user is not None:
    #         db.delete(user)
    #     return user

    # def get_user_byid(self, db: Session, user_id: int) -> UserModel:
    #     return db.query(UserModel).filter(UserModel.user_id == user_id).first()

    async def get_all_users(self) -> List[list]:
        s = UserModel.select()
        res = await db.fetch_all(query=s)
        # print(res)
        return [row for row in res]
