import os
import logging
import functools

from app.config import appconfig, Environment

from app.database.database import QuestionnaireDatabaseManager

from . import root

logger = logging.getLogger(__name__)

db = QuestionnaireDatabaseManager.create(
    appconfig=appconfig,
    folder=os.path.join(root, "app", "database", "sql"),
    sql_files=[
        "users.sql",
    ],
)

logger.warning("Initialise database schema...")

## for ddog
tracer = None
datadog_middleware = None