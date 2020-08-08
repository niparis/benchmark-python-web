import logging

import falcon

logger = logging.getLogger(__name__)


class MissingAttribute(Exception):
    pass


class ObjectCreationError(Exception):
    @staticmethod
    def handle(ex, req, resp, params):
        # TODO: Log the error
        logger.exception("Object Creation Error:")
        raise falcon.HTTPBadRequest(title="Entity creation Error", description=str(ex))


class ValidationError(Exception):
    @staticmethod
    def handle(ex, req, resp, params):
        # TODO: Log the error
        logger.exception("Validation Error:")
        raise falcon.HTTPBadRequest(title="Validation Error", description=str(ex))
