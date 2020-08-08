import logging
import datetime as dt


logger = logging.getLogger(__name__)


class ResponseLoggerMiddleware(object):
    def process_request(self, req, resp):
        logger.warning(f"{req.method}] {req.relative_uri} - received")
        req.context["start_time"] = dt.datetime.now()

    def process_response(self, req, resp, *args, **kwargs):
        duration = (
            dt.datetime.now() - req.context["start_time"]
        ).total_seconds() * 1000
        logger.warning(
            f"{req.method}] {req.relative_uri} {resp.status[:3]} - {duration:.2f} ms [{req.access_route[0]}]"
        )
        if resp.status[:3] in ("401", "403"):
            logger.error(f"Posted headers: {req.headers}")
