import secrets
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import (
    AnyHttpUrl,
    BaseSettings,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    validator,
)
from starlette.datastructures import CommaSeparatedStrings, Secret


class Settings(BaseSettings):
    CODE_PATH: Path = Path(__file__).parents[2]

    DDL_PATH: Path = CODE_PATH / "app" / "infrastructure" / "database" / "ddl"
    MODELS_PATH: Path = CODE_PATH / "app" / "infrastructure" / "database" / "models"

    DB_NAME: str = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432

    # SQLALCHEMY_DATABASE_URI: PostgresDsn = f'postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("DB_USER"),
            password=values.get("DB_PASSWORD"),
            host=values.get("DB_HOST"),
            port=str(values.get("DB_PORT")),
            path=f"/{values.get('DB_NAME') or ''}",
        )

    SENTRY_DSN: Optional[str] = None

    class Config:
        env_file = ".env"  # p: Path = Path(__file__).parents[2] / ".env"
        case_sensitive = True


settings = Settings()
