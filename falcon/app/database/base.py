from app.database.pycrudorm import CRUD
from app.connections import db


class BaseObject(CRUD):
    db = db
