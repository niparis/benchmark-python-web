import datetime as dt
from typing import Any, List

import pytest
from fastapi import FastAPI
from starlette import status
from starlette.testclient import TestClient

from app.models.orm.user import User as UserDB
from app.models.pydantic.user import User, UserCreateIn, UserUpdateIn
from app.routes.users import router


def create_test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)

    return app


app = create_test_app()
client = TestClient(app)

USER_MODEL = User(
    name="bob",
    email="bob@microsoft.usa",
    phone_number="90909090",
    country_code="SG",
)


@pytest.fixture
def user_model() -> User:
    return USER_MODEL


@pytest.fixture
def user_schema() -> UserDB:
    return UserDB(
        name="bob",
        email="bob@microsoft.usa",
        phone_number="90909090",
        country_code="SG",
    )


class TestUserRouter:
    def test_user_create_valide(
        self, user_model: User, user_schema: UserDB
    ) -> None:

        response = client.post(
            "/users",
            json={
                "name": "bob",
                "email": "bob@microsoft.usa",
                "phone_number": "90909090",
                "country_code": "SG",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == user_schema.__dict__
