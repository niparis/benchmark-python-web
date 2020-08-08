from sqlalchemy.orm import Session

from app.domain.users.users_service import UserService
from app.infrastructure.database.queries.user import UserQueries


def get_user_services() -> UserService:
    return UserService(UserQueries())
