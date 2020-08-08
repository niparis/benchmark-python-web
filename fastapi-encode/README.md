# getting started

you need postgres (postgresapp)

## first time
cp .dist.env .env
psql -c "create database asyncfast;"
poetry install
poetry shell
poetry run task manage sync-db
poetry run task app-prod

## later

psql -d asyncfast -c "truncate table users;"
poetry shell
poetry run task app-prod


python -m vmprof --config vmprof.ini --web ./run.sh