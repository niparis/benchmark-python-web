import sys

from gunicorn.app.base import BaseApplication
from gunicorn.workers.sync import SyncWorker
import rollbar

from .app import FalconService
from .config import appconfig


class CustomWorker(SyncWorker):
    def handle_quit(self, sig, frame):
        self.app.application.stop(sig)
        super(CustomWorker, self).handle_quit(sig, frame)

    def run(self):
        self.app.application.start()
        super(CustomWorker, self).run()

    def handle_error(self, req, client, addr, exc):
        rollbar.report_exc_info(
            sys.exc_info(), req, extra_data={"client": client, "uri": req.uri}
        )
        super(CustomWorker, self).handle_error(req, client, addr, exc)


class GunicornApp(BaseApplication):
    """ Custom Gunicorn application

    This allows for us to load gunicorn settings from an external source
    """

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(GunicornApp, self).__init__()

    def load_config(self) -> None:
        for key, value in self.options.to_dict.items():
            self.cfg.set(key.lower(), value)

        self.cfg.set("worker_class", "app.wsgi.CustomWorker")

    def load(self) -> FalconService:
        return self.application


def main() -> None:

    api_app = FalconService()
    gunicorn_app = GunicornApp(api_app, appconfig.gunicorn)

    gunicorn_app.run()
