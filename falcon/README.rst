Run the project


You need to have postgres running

A. first time
psql -c "create database falcon;"
poetry install
poetry shell
python manage.py initdb
python manage.py run

A. later

poetry shell
python manage.py run