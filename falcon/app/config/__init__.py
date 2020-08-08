import logging
import os

from .config import ServiceConfig, Environment  # noqa
from .config import DbConfig, GunicornConfig, AppConfig

logger = logging.getLogger(__name__)


def load_config(test=False) -> ServiceConfig:

    # dumb version
    db_config = DbConfig(
        # host=os.getenv("HP__DB_HOST", ""),
        # port=os.getenv("HP__DB_PORT", ""),
        # user=os.getenv("HP__DB_USERNAME", ""),
        # password=os.getenv("HP__DB_PASSWORD", ""),
        # dbname=os.getenv("HP__DB_DBNAME", ""),
    )

    gunicorn_config = GunicornConfig(
        # bind=os.getenv("HP__GUNICORN_BIND"),
        # workers=os.getenv("HP__GUNICORN_WORKERS"),
        # timeout=os.getenv("HP__GUNICORN_TIMEOUT"),
        # reload=bool(os.getenv("HP__GUNICORN_RELOAD")),
    )

    app_config = AppConfig(
        # salt=os.getenv("HP__APP_SALT"),
        # secret_iv=os.getenv("HP__APP_SERCRET_IV"),
        # amplitude=os.getenv("HP__APP_AMPLITUDE"),
        # braze=os.getenv("HP__APP_BRAZE"),
        # rollbar=os.getenv("HP__APP_ROLLBAR"),
        # environment=Environment(os.getenv("HP__APP_ENVIRONMENT")),
        # analytics_cache_threshold=os.getenv("HP__ANALYTICS_CACHE_THRESHOLD"),
    )

    return ServiceConfig(
        db=db_config,
        app=app_config,
        gunicorn=gunicorn_config,
    )


appconfig = None


def init(test=False):
    global appconfig
    logger.warning(f"Loading settings, test was {test}")
    appconfig = load_config(test=test)
    logger.warning(
        f"Config loaded with environment set to: {appconfig.app.environment}"
    )


if appconfig is None:
    init()
