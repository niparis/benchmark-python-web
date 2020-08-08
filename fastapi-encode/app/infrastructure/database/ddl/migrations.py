import os

from app.core.config import settings
from app.core.db import db
from app.main import create_app


def read_sql(fname: str) -> str:
    with open(
        os.path.join(
            settings.CODE_PATH,
            "app",
            "infrastructure",
            "database",
            "ddl",
            fname,
        ),
        "r",
    ) as fout:
        return fout.read()


def execute_primary():
    sql = read_sql("main.sql")
    print("start")
    with db.acquire() as conn:
        promo_audit = conn.raw_connection.execute(sql)

    print(promo_audit)
