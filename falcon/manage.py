import os
import logging

import click

from app import __version__ as version
from app import wsgi
from app.app import FalconService
from app.config import appconfig

path = os.path.dirname(os.path.realpath(__file__))

logger = logging.getLogger(__name__)


@click.group()
def cli() -> None:
    """Questionnaire-Backend Command Line Manager"""

    logger.warning(f'Questionnaire-Service version {version} [initated]')


@click.option('--port', type=int, default=8000)
@click.option('--profile', is_flag=True, default=False)
@cli.command()
def dev(profile, port) -> None:
    """ Runs a debug test server for development """
    from werkzeug.serving import run_simple

    application = FalconService()
    application.start()


    logger.warning(f'Running the debug server on port {port}')
    run_simple('0.0.0.0', port, application, use_reloader=True, use_debugger=False)


@cli.command()
def run() -> None:
    """Runs the application with Gunicorn"""

    logger.warning(
        f'Running questionnaire-service with gunicorn, settings: {appconfig.app.environment}')

    wsgi.main()


@cli.command()
def initdb() -> None:
    """ Create tables, mat views and base data """

    application = FalconService()
    application.db.init_db()



if __name__ == "__main__":
    cli()
