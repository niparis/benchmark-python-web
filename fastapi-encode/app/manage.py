import subprocess  # nosec
import sys

import click

sys.path.extend(["./", "../"])


@click.group("Fast-api App manager")
def manage() -> None:
    # the main group of commands
    pass


@manage.command(help="init db")
def sync_db() -> None:
    """
        Syncs the DDL with the database, and generates sqlalchemy models
    """
    from app.core.config import settings
    from app.utils.migrations import sync, export_all_tables

    sync(settings)
    export_all_tables(settings)


@manage.command(help="export models")
def export_models() -> None:
    from app.core.config import settings
    from app.utils.migrations import export_all_tables

    export_all_tables(settings)


if __name__ == "__main__":
    manage()
