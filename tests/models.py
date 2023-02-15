import datetime

from sqlalchemy import Column, String, DateTime, Float, Integer
from sqlalchemy.orm import declarative_base

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
