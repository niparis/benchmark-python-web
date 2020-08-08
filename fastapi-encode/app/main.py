# isort:skip_file
import logging
import sys

sys.path.extend(["./"])

from sentry_sdk import init as initialize_sentry
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.datastructures import Secret
from fastapi import FastAPI

# from app.application import app
from app.api.api import api_router
from app.core.config import settings
from app.core.db import db
from app.utils.middleware import PerformanceMonitoringMiddleware

# from app.core.db import db


logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    if settings.SENTRY_DSN.__str__() not in ("None", ""):
        initialize_sentry(
            dsn=settings.SENTRY_DSN.__str__(),
            integrations=[SqlalchemyIntegration()],
        )

    logger.info("Initiliase fast-API app")
    app = FastAPI(on_startup=[db.connect], on_shutdown=[db.disconnect])
    # db.init_app(app=app)
    app.include_router(api_router)

    if settings.SENTRY_DSN.__str__() not in ("None", ""):
        app.add_middleware(SentryAsgiMiddleware)

    app.add_middleware(PerformanceMonitoringMiddleware)

    return app


try:
    app = create_app()
except Exception as e:
    logger.error(f"Error in fast-API app initialisation => {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="info")
