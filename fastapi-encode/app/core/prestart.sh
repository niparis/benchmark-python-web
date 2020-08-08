#!/usr/bin/env bash
# alembic upgrade head
# source $HOME/.poetry/env && poetry run task manage sync-db
sleep 3 && python app/manage.py sync-db