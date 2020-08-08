import related
import enum

# related doc : https://github.com/genomoncology/related/


class Environment(enum.Enum):
    dev = "dev"
    test = "test"
    production = "production"
    ci = "ci"


class Borg(object):
    _state = {}

    def __new__(cls, *p, **k):
        if "_the_instance" not in cls.__dict__:
            cls._the_instance = object.__new__(cls)
        return cls._the_instance


@related.immutable
class DbConfig(object):
    host = related.StringField(default="localhost")
    port = related.IntegerField(default=5432)
    user = related.StringField(default="nicolasparis")
    password = related.StringField(default="password")
    dbname = related.StringField(default="falcon")
    echo_sql = related.BooleanField(default=False)

    @property
    def sqlalchemy_database_uri(self):
        return f"postgres://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}?application_name=falcon"

    @property
    def sqlalchemy_database_uri_nodb(self):
        return f"postgres://{self.user}:{self.password}@{self.host}:{self.port}/postgres?application_name=falcon"


@related.immutable
class GunicornConfig(object):
    bind = related.StringField(default="localhost:8000")
    workers = related.IntegerField(default=1)
    timeout = related.IntegerField(default=3000)
    reload = related.BooleanField(default=False)

    @property
    def to_dict(self):
        return related.to_dict(self)


@related.immutable
class AppConfig(object):
    rollbar = related.StringField(required=False, default=None)
    environment = related.ChildField(Environment, default=Environment.dev)
    caching = related.IntegerField(default=1)
    cors_enabled = related.BooleanField(default=False)
    cors_allowed_host = related.StringField(required=True, default="localhost")
    host = related.StringField(required=True, default="http://localhost:8001")

@related.immutable
class ServiceConfig(Borg):
    service_name = related.StringField(default="questionnaire-service")
    db = related.ChildField(DbConfig, default=DbConfig())
    app = related.ChildField(AppConfig, default=AppConfig())
    gunicorn = related.ChildField(GunicornConfig, default=GunicornConfig())
