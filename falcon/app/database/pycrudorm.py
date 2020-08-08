import logging
import os
import typing
from typing import List, Dict, Tuple, Any

import falcon
import sqlalchemy
import sqlalchemy as sqla
from sqlalchemy import orm
import attr
from ddtrace import Pin, patch, tracer

logger = logging.getLogger(__name__)


@attr.s(auto_attribs=True)
class DataBaseManager(object):
    dburi: str
    engine: None = attr.ib(repr=False)
    queries: Dict[str, str] = attr.ib(repr=False)
    DBSession: None = attr.ib(repr=False)
    connection: None = attr.ib(repr=False, default=None)
    ready: bool = attr.ib(default=False)
    base: typing.Any = attr.ib(default=None)

    @classmethod
    def create(cls, *args, appconfig, folder: str, sql_files: List[str], **kargs):
        from ..config import Environment

        # For datadog APM
        if appconfig.app.environment in (Environment.production, Environment.test):
            patch(sqlalchemy=True)

        dburi = appconfig.db.sqlalchemy_database_uri
        logger.warning(
            f"Preparing connection to database {appconfig.db.dbname} on host {appconfig.db.host}"
        )
        engine = sqla.create_engine(dburi, echo=appconfig.db.echo_sql)

        # For datadog APM
        if appconfig.app.environment in (Environment.production, Environment.test):
            logger.info("starting datadog (APM)")
            Pin.override(engine, service="questionnaire-service-db")

        DBSession = orm.scoping.scoped_session(
            orm.sessionmaker(bind=engine, autocommit=True)
        )

        queries = cls._read_queries(folder=folder, sql_files=sql_files)

        return cls(
            dburi=dburi, engine=engine, queries=queries, DBSession=DBSession, base=None
        )

    def connect(self):
        counter = 0
        import time

        while True:
            try:
                self._connect()
                return None
            except sqlalchemy.exc.OperationalError:
                counter += 1
                if counter > 4:
                    break
                wait_time = (1 + counter) ** 2
                logger.exception(
                    f"Database connection error, waiting: {wait_time} secs"
                )
                time.sleep(wait_time)

        logger.critical("Too many database connection erors, exiting")
        raise Exception("Cant connect to database")

    def _connect(self):
        from sqlalchemy.ext.automap import automap_base

        Base = automap_base()

        Base.prepare(self.engine, reflect=True, schema="question")

        self.connection = self.engine.connect()
        logger.warning("Connected to database")

        self.ready = True
        self.base = Base

    def stop(self):
        self.connection.close()

    def get_sa_table(self, table: str) -> sqlalchemy.sql.schema.Table:
        try:
            return getattr(self.base.classes, table).__table__
        except AttributeError:
            return None

    @property
    def session(self):
        return self.DBSession()

    def execute_dynamic_query(self, query_name: str, dynamic: dict, parameters: dict):
        """
            dynamic: set of parameters that will be used to format the query
            parameters: set of parameters that will be sent to
        """
        sql = self._get_query(query_name).format(**dynamic)

        # logger.warning(sql)
        # logger.info(parameters)
        return self.execute_raw_sql(sql, **parameters)

    def execute_file(self, query, **kwargs):
        sql = self._get_query(query_name=query)
        with self.connection.begin():
            res = self.connection.execute(sqla.sql.text(sql), **kwargs)
        return res

    def execute_raw_sql(self, sql, **kwargs):
        with self.connection.begin():
            res = self.connection.execute(sqla.sql.text(sql), **kwargs)

        return res

    def execute_direct_file(self, path):
        with open(path, "r") as fin:
            sql = fin.read()

        return self.execute_raw_sql(sql=sql)

    def execute_sqla(self, statement):
        with self.connection.begin():
            try:
                res = self.connection.execute(statement)
            except sqla.exc.ProgrammingError as ex:
                logger.exception(f"could not execute: {statement}")
                raise ex
            except Exception as ex:
                logger.exception("could not execute")
                raise ex

        return res

    def _get_query(self, query_name: str) -> str:
        if query_name in self.queries:
            return self.queries[query_name]
        else:
            logger.critical(
                "%s no available. Queries loaded: %s",
                query_name,
                ", ".join(self.queries),
            )
            raise ValueError("Could not find query %s", query_name)

    @staticmethod
    def _read_queries(folder: str, sql_files: str) -> Dict[str, str]:
        """ Read all the queries from a file organized in the same way than anosql
            Each query MUST start with the following token "-- name:"
                The text after will be the query's name
                The query itself should start on the following line
        """
        queries = {}
        for sql in sql_files:
            with open(os.path.join(folder, sql), "r") as fin:
                data = fin.read()

            rows = [r for r in data.split("\n")]
            for row in rows:
                if "-- name:" in row:
                    key = row.split("-- name:")[1].strip()
                    if key in queries:
                        raise Exception("the query %s is present in another file!", key)
                    queries[key] = ""
                elif len(row) > 0:
                    queries[key] += row + "\n"

        return queries


class CRUD(object):
    db = None

    @classmethod
    def pk(cls, *args, **kwargs) -> List:
        pk_or_unique = []
        for col in cls._table.columns:
            if col.primary_key:
                pk_or_unique.append(col)
        for col in cls._table.columns:
            if col.unique:
                pk_or_unique.append(col)

        return pk_or_unique

    @classmethod
    def _constructor(cls, res):
        return cls(**res)

    @staticmethod
    def pk_dict_to_tuple(pk: dict) -> tuple:
        col = list(pk.keys())[0]
        val = pk[col]
        return col, val

    @classmethod
    @tracer.wrap(service="questionnaire-service")
    def load(cls, **kwargs):
        logger.info(f"{cls} - PYCRUD- LOAD")
        pk_or_unique = cls.pk()
        column, value = None, None

        for col in pk_or_unique:
            if col.name in kwargs:
                column = col.name
                value = kwargs[col.name]

        if column is None:
            raise ValueError(
                "Load only works with a argument (primary key or unique col) "
            )

        stmt = sqla.sql.select(cls._table.c).where(
            getattr(cls._table.c, column) == value
        )
        res = cls.db.execute_sqla(stmt).first()

        if res is None:
            logger.error(f"no row for class {cls} with pk {column}={value}")
            return None
        return cls._constructor(res)

    @classmethod
    @tracer.wrap(service="questionnaire-service")
    def load_from_all_args(cls, table, **kwargs):
        """Will try to load an object with all the passed args"""
        table = cls.db.get_sa_table(table)
        lt = [getattr(table.c, column) == value for column, value in kwargs.items()]
        stmt = sqla.sql.select(table.c).where(sqla.sql.and_(*lt))
        res = cls.db.execute_sqla(stmt)
        if res.rowcount > 1:
            logger.error(f"got more than one row for class {cls} and args {kwargs}")
            return None

        if res.rowcount == 0:
            logger.error(f"no row for class {cls} with args {kwargs}")
            return None

        return cls._constructor(res.first())

    @classmethod
    @tracer.wrap(service="questionnaire-service")
    def create(cls, **kwargs):
        stmt = cls._table.insert().values(**kwargs)
        try:
            res = cls.db.execute_sqla(stmt)
        except sqla.exc.IntegrityError as ex:
            res = False
            logger.exception("Already exists")
            raise ex
        except sqla.exc.CompileError as ex:
            logger.exception("Could not compile. Some extra column ?")
            raise ValueError(str(ex))

        if res is False:
            return False

        try:
            ret = cls.load(**kwargs)
        except ValueError:
            logger.exception("could not load")
            ret = True

        return ret

    @tracer.wrap(service="questionnaire-service")
    def delete(self):
        pk = self.pk()[0]
        stmt = self._table.delete().where(pk == getattr(self, pk.name))
        self.db.execute_sqla(stmt)

    @tracer.wrap(service="questionnaire-service")
    def update(self, **kwargs):
        for col, val in kwargs.items():
            setattr(self, col, val)

        pk = self.pk()[0]
        try:
            stmt = (
                self._table.update()
                .values(**kwargs)
                .where(pk == getattr(self, pk.name))
            )
        except sqlalchemy.exc.CompileError as ex:
            missing_col = str(ex).split(":")[1]
            raise ValueError(
                f"trying to updated column {missing_col} which does not exist in db"
            )

        try:
            self.db.execute_sqla(stmt)
        except sqla.exc.IntegrityError as ex:
            logger.exception("Already exists")
            raise ex

    @classmethod
    @tracer.wrap(service="questionnaire-service")
    def load_or_create(cls, **kwargs) -> Tuple[bool, Any]:
        """ Returns a tuple, where the:
              - first element: true if created, false if already existing
              - second element: the loaded object
        """
        obj = cls.load(**kwargs)
        logger.debug("loaded")
        created = False
        if not obj:
            logger.debug("creating")
            obj = cls.create(**kwargs)
            created = True

        if not created:
            different_attributes = {}
            for col, val in kwargs.items():
                if val != getattr(obj, col):
                    different_attributes[col] = val

            if different_attributes:
                logger.debug("updating")
                obj.update(**kwargs)

        return created, obj

    @classmethod
    def load_or_404(cls, **kwargs):
        obj = cls.load(**kwargs)
        if not obj:
            raise falcon.HTTPNotFound(
                description=f"No {cls.__name__} found with params %r" % kwargs
            )

        return obj
