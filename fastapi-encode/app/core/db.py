import logging

from databases import Database

from app.core.config import settings

# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker


logger = logging.getLogger(__name__)

db = Database(settings.SQLALCHEMY_DATABASE_URI)
