import logging

import falcon
from falcon_cors import CORS
from falcon_auth import FalconAuthMiddleware
import rollbar
from falcon import media
import rapidjson
from functools import partial
from rapidjson import DM_ISO8601, UM_CANONICAL, NM_DECIMAL

# from .database.manager import db
from app.config import appconfig, Environment


from app.controllers.users_controller import UsersManager, UsersListManager

from app.lib.middleware import ResponseLoggerMiddleware
from app.lib.exceptions import ValidationError, ObjectCreationError
from app.lib.validation import CustomJSONHandler
from app.connections import db, datadog_middleware
from app import __version__

logger = logging.getLogger(__name__)


class FalconService(falcon.API):
    def __init__(self, *args, **kargs):
        # database manager
        self.db = db

        if appconfig.app.environment in [
            Environment.production.value,
            Environment.test.value,
        ]:
            logger.warning("rollbar init")
            rollbar.init(appconfig.app.rollbar, environment=appconfig.app.environment)
        else:
            logger.warning("rollbar not started")

        # Authentication
        # auth_middleware = FalconAuthMiddleware(
        #     AUTH_BACKEND, exempt_methods=["HEAD", "OPTIONS"], exempt_routes=["/auth/"]
        # )

        # setting up cors
        cors_parameters = {"allow_all_headers": True, "allow_all_methods": True}
        if appconfig.app.cors_enabled:
            logger.warning("CORS is enabled")
            cors_parameters["allow_origins_list"] = appconfig.app.cors_allowed_host
        else:
            logger.warning("NO CORS")
            cors_parameters["allow_all_origins"] = True

        cors = CORS(**cors_parameters)
        # preparing the final list of middlewares
        list_middlewares = [
            ResponseLoggerMiddleware(),
            cors.middleware,
            # auth_middleware,
        ]

        # For datadog APM
        if datadog_middleware:
            list_middlewares.append(datadog_middleware)

        # load all middlewares
        super().__init__(middleware=list_middlewares)

        # error handlers
        self.add_error_handler(ValidationError, ValidationError.handle)
        self.add_error_handler(ObjectCreationError, ObjectCreationError.handle)

        # custom media handlers

        json_handler = media.JSONHandler(
            dumps=partial(
                rapidjson.dumps,
                ensure_ascii=False, sort_keys=True,  datetime_mode=DM_ISO8601
            ),
        )        
        extra_handlers = {
            'application/json': json_handler,
        }        
        # handlers = falcon.media.Handlers({"application/json": CustomJSONHandler()})

        self.req_options.media_handlers.update(extra_handlers)
        self.resp_options.media_handlers.update(extra_handlers)

        # Questionnaire Endpoints
        # fmt: off
        class RootResource:
            auth = {"exempt_methods": ["GET"]}

            def on_get(self, req, resp):
                resp.media = {
                    'service-version': __version__,
                    'service-name': 'questionnaire-service',
                }

        self.add_route(
            "/",
            RootResource()
        )
        # -- answer endpoints --
        # This is in use currently by most system
        self.add_route(
            "/users",
            UsersManager()
        )    
        self.add_route(
            "/users/all",
            UsersListManager()
        )        
        print('all routes')    
        # fmt: on

    def start(self):
        """ A hook to when a Gunicorn worker calls run()."""
        self.db.connect()

    def stop(self, signal):
        """ A hook to when a Gunicorn worker starts shutting down. """
        self.db.stop()
