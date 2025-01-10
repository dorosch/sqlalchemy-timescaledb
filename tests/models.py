import datetime
import os

from sqlalchemy import Column, String, DateTime, Float, Integer
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base

DATABASE_URL = URL.create(
    host=os.environ.get('POSTGRES_HOST', 'localhost'),
    port=os.environ.get('POSTGRES_PORT', 5432),
    username=os.environ.get('POSTGRES_USER', 'postgres'),
    password=os.environ.get('POSTGRES_PASSWORD', 'password'),
    database=os.environ.get('POSTGRES_DB', 'test_timescaledb'),
    drivername=os.environ.get('DRIVERNAME', 'timescaledb')
)

Base = declarative_base()


class Metric(Base):
    __tablename__ = 'metrics'
    __table_args__ = (
        {
            'timescaledb_hypertable': {
                'time_column_name': 'timestamp'
            }
        }
    )

    id = Column(Integer, primary_key=True , autoincrement=True)
    name = Column(String)
    value = Column(Float)
    timestamp = Column(
        DateTime(), default=datetime.datetime.now, primary_key=True
    )


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
