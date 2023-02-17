import datetime
import os

from sqlalchemy import Column, String, DateTime, Float, Integer
from sqlalchemy import create_engine
from sqlalchemy.dialects import registry
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

registry.register(
    'timescaledb',
    'sqlalchemy_timescaledb.dialect',
    'TimescaledbPsycopg2Dialect'
)
registry.register(
    'timescaledb.psycopg2',
    'sqlalchemy_timescaledb.dialect',
    'TimescaledbPsycopg2Dialect'
)
registry.register(
    'timescaledb.asyncpg',
    'sqlalchemy_timescaledb.dialect',
    'TimescaledbAsyncpgDialect'
)

engine = create_engine(
    URL.create(
        host=os.environ.get('POSTGRES_HOST', '0.0.0.0'),
        port=os.environ.get('POSTGRES_PORT', 5432),
        username=os.environ.get('POSTGRES_USER', 'user'),
        password=os.environ.get('POSTGRES_PASSWORD', 'password'),
        database=os.environ.get('POSTGRES_DB', 'database'),
        drivername=os.environ.get('DRIVERNAME', 'timescaledb')
    )
)
Session = scoped_session(sessionmaker(bind=engine))
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
