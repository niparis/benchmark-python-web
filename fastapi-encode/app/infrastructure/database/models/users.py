# coding: utf-8
from sqlalchemy import BigInteger, Boolean, Column, DateTime, MetaData, String, Table, text

metadata = MetaData()


t_users = Table(
    'users', metadata,
    Column('user_id', BigInteger, primary_key=True, server_default=text("nextval('\"public\".users_user_id_seq'::regclass)")),
    Column('email', String, unique=True),
    Column('full_name', String),
    Column('password', String),
    Column('is_active', Boolean, nullable=False, server_default=text("true")),
    Column('is_superuser', Boolean, nullable=False, server_default=text("false")),
    Column('created_date', DateTime, nullable=False, server_default=text("now()")),
    schema='public'
)
