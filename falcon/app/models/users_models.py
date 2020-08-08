import logging
from typing import Optional, Tuple, List
import json
import datetime as dt

import sqlalchemy
import falcon
import attr
import rollbar


from ..config import appconfig
from app.lib.exceptions import ValidationError, ObjectCreationError

from app.database.base import BaseObject
from app.database.models import sqla_models

from app.lib.validation import ValidatedObject, ValidatedEntity, second_to_datetime
from datetime import datetime

logger = logging.getLogger(__name__)


  
@attr.s(auto_attribs=True, slots=True)
class User(BaseObject, ValidatedObject):
    """ Represents the posted questionnaire payload.
        Should only be read in case of debugging.
    """

    user_id: int
    full_name: str
    email: str
    password: str    
    is_active: bool = True
    is_superuser: bool = False
    created_date: datetime = attr.ib(default=datetime.utcnow())

    _table = sqla_models.t_users


    def __attrs_post_init__(self, *args, **kwargs):
        super().__init__()

    # @classmethod
    # def _constructor(cls, res):
    #     return cls(
    #         userid=res["userid"],
    #         country=res["country"],
    #         lang=res["lang"],
    #         prophy=res["prophy"],
    #         chronicity=res["chronicity"],
    #         migraine_years=res["migraine_years"],
    #     )


    @classmethod
    def get_all(cls):
        """
        """
        # for x in cls.db.execute_file("get-all-users").fetchall():
            # print(x)

        return [cls(*x) for x in cls.db.execute_file("get-all-users").fetchall()]


