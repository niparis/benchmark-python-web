import os
import logging
import csv
import sqlalchemy

from .. import root as project_root
from .pycrudorm import DataBaseManager
from ..config import appconfig

logger = logging.getLogger(__name__)


class QuestionnaireDatabaseManager(DataBaseManager):
    def init_db(self):
        """
            initialise a database based on the DDL and migration history given
        """
        super().connect()

        # structure initialisation
        self._init_base_schema()

        super().stop()

    def _init_base_schema(self):
        logger.info("Initialising base schema ...")

        path = os.path.join(project_root, "app/database/sql/db-creation.sql")

        try:
            self.execute_direct_file(path)
        except sqlalchemy.exc.ProgrammingError as ex:
            if "already" in str(ex):
                logger.warning("Database already exits.")
            else:
                raise ex

        logger.info("Base schema initialised.")
