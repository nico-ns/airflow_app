from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String, ForeignKey, Float, Boolean, Numeric, DateTime

# SQL ALCHEMY SECTION: MODELS FOR DB TABLES
metadata_obj = MetaData()

Users = Table(
    "users",
    metadata_obj,
    Column('user_id', String(36), primary_key=True),
    Column('storage', Numeric(precision=None, scale=3)),
    Column('created', DateTime())
)

Events = Table(
    "events",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column('user_id', String(36), ForeignKey('users.user_id')),
    Column('direction', String, nullable=False),
    Column('status', String, nullable=False),
    Column('size', Numeric(precision=None, scale=0)),
    Column('timestamp', Numeric(precision=None, scale=0)),
    Column('transfer_time', Numeric(precision=None, scale=0)),
    Column('transfer_speed', Numeric(precision=None, scale=2))
)