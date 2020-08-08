import json
import enum
import logging
import datetime as dt
from typing import Dict, Any

import attr
import sqlalchemy
import falcon

# from falcon import errors
from falcon.media import BaseHandler
from sqlalchemy.orm import Session

from app.lib.exceptions import ObjectCreationError, MissingAttribute
from app.connections import tracer

logger = logging.getLogger(__name__)


class GetSingleRecord(object):
    @classmethod
    def get_single_record(cls, session: Session, **kwargs) -> bool:

        try:
            ret_val = session.query(cls).filter_by(**kwargs).one()
        except sqlalchemy.orm.exc.NoResultFound:
            ret_val = False
        except sqlalchemy.orm.exc.MultipleResultsFound:
            raise ValueError(
                f"multiple records found for {cls.__name__} and arguments {kwargs}"
            )

        return ret_val


class GetOrCreate(object):
    @classmethod
    def get_or_create(cls, session: Session, **kwargs) -> object:
        try:
            ret_val = session.query(cls).filter_by(**kwargs).one()
        except sqlalchemy.orm.exc.NoResultFound:
            ret_val = cls(**kwargs)
        except sqlalchemy.orm.exc.MultipleResultsFound:
            logger.critical("Multiple results found with data point %r" % kwargs)
            raise

        return ret_val


class ValidatedObject(object):
    _creation_attributes = None

    @classmethod
    def from_dict(cls, *args, **kwargs):
        creation_attributes = list(kwargs.keys())
        try:
            obj = cls(*args, **kwargs)
            obj._creation_attributes = creation_attributes
            return obj
        except ValueError as ex:
            raise ObjectCreationError(str(ex))
        except TypeError as ex:

            if "multiple" in str(ex):
                raise ObjectCreationError(
                    f"Please pass only keywords arguments to create {cls.__name__}"
                )
            if "missing" in str(ex):
                if "arguments:" in str(ex):
                    missing_keys = str(ex).split("arguments:")[1]
                elif "argument:" in str(ex):
                    missing_keys = str(ex).split("argument:")[1]
                else:
                    raise ex

                raise ObjectCreationError(
                    f"Missing some key(s): {missing_keys} when creating {cls.__name__}"
                )

            print(ex)
            unexpected_key = str(ex).split("argument")[1]
            raise ObjectCreationError(
                f"key {unexpected_key} does not exist when creating {cls.__name__}"
            )

    @property
    def as_dict(self):
        return attr.asdict(self)

    @property
    def as_dict_not_null(self):
        adict = {k: v for k, v in self.as_dict.items() if v is not None}

        if self._creation_attributes:
            for attribute in self._creation_attributes:
                if attribute not in adict:
                    adict[attribute] = None

        return adict


class ValidatedEntity(ValidatedObject):
    @classmethod
    def attribute(cls, value):
        if value in cls.__annotations__:
            return value

        raise MissingAttribute(f"attribute {value} not found in class {cls}")

    @classmethod
    def from_dict(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    @classmethod
    def from_dict_safe(cls, *args, **kwargs):

        try:
            return cls.from_dict(*args, **kwargs)
        except (ValueError, AssertionError) as ex:
            raise ObjectCreationError(str(ex))
        except TypeError as ex:

            if "multiple" in str(ex):
                raise ObjectCreationError(
                    f"Please pass only keywords arguments to create {cls.__name__}"
                )
            elif "missing" in str(ex):
                try:
                    missing_keys = str(ex).split("arguments:")[1]
                except Exception as ex:
                    missing_keys = str(ex).split("argument:")[1]

                raise ObjectCreationError(
                    f"Missing some key(s): {missing_keys} when creating {cls.__name__}"
                )
            elif "must be" in str(ex):
                msg = str(ex).split(">")[0]
                raise ObjectCreationError(f"{msg}>")
            else:
                raise ObjectCreationError(f"unhandled object creation error: {str(ex)}")

            unexpected_key = str(ex).split("argument")[1]
            raise ObjectCreationError(
                f"key {unexpected_key} does not exist when creating {cls.__name__}"
            )


class ValidateRequest(object):
    def __init__(self, entity):
        self._entity = entity  # should be a subclass of ValidatedEntity

    def __call__(self, req, resp, resource, params):
        try:
            payload = req.media
        except KeyError:
            payload = {}
        except Exception:
            raise
        instance = self._entity.from_dict_safe(req=req, **payload)
        key = self.convert(self._entity.__name__)
        params[key] = instance

    def convert(self, name):
        import re

        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


class PostgresEnum(enum.Enum):
    """ Used to represent a database enum

        Subclass and load a string coming from a Enum database column

        class EnumTest(PostgresEnum):
            type_one = "one"
            type_two = "two"

        >> EnumTest.load("one")
        <EnumTest.type_one: 'one'>

        >> EnumTest.load("xxxx")
        ValueError: xxxx is not part of the enum <enum 'EnumTest'>

    """

    def __str__(self):
        return str(self.value)

    @classmethod
    def ok_values(cls):
        return ", ".join(
            [str(member.value) for name, member in cls.__members__.items()]
        )

    @classmethod
    def load(cls, value: str, none_ok: bool = False):
        # value should be a string, as loaded from a database
        if none_ok and value is None:
            return None

        for name, member in cls.__members__.items():
            if member.value == value or member == value:
                return member

        raise ValueError(
            f"{value} is not part of the enum {cls}. must be one of {cls.ok_values()}"
        )


class CustomJSONHandler(BaseHandler):
    """Handler built using Python's :py:mod:`json` module."""

    def deserialize(self, raw, content_type, content_length):
        try:
            return json.loads(raw.decode("utf-8"))
        except ValueError as err:
            raise falcon.HTTPBadRequest(
                title="Invalid JSON",
                description="Could not parse JSON body - {0}".format(err),
            )

    def serialize(self, media, content_type):
        try:
            result = json.dumps(media, ensure_ascii=False, default=str)
        except TypeError as ex:
            logger.exception(f"error when serializing {media}")
            raise ex
        if not isinstance(result, bytes):
            return result.encode("utf-8")

        return result


def admin_only(req, resp, resource, params):
    """To be used as a before_hook. Only admins will be allowed to use this endpoint"""

    if "user" not in req.context:
        raise falcon.HTTPUnauthorized()

    user = req.context["user"]
    if not user.is_admin:
        raise falcon.HTTPForbidden(description="admin only endpoint")


def construct_cache_key_for_insights(questionnaireid: int, country: str) -> str:
    """ recreate the cache key for insights """
    segmentation_for_insights = {"country": country}
    answer_type = "choiceid"
    return f"{questionnaireid}-{str(segmentation_for_insights)}-{answer_type}"


def add_info_to_data_dog(info: Dict[str, Any]) -> None:
    """
        Sends extra info to datadog
        Doc: https://docs.datadoghq.com/tracing/guide/add_span_md_and_graph_it/?tab=python
    """
    current_span = tracer.current_span()
    if current_span:
        for tag, value in info.items():
            current_span.set_tag(tag, value)
    else:
        logger.error("Could not get current_span in add_info_to_data_dog")


def second_to_datetime(epoch_in_s: int) -> dt.datetime:
    """
        This function assumes the epoch past
        in is in seconds
    """
    return dt.datetime.utcfromtimestamp(epoch_in_s)
