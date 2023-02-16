import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.dialects import registry
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, scoped_session

from tests.models import Base


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


def pytest_configure(config):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def session():
    yield Session


@pytest.fixture
def is_hypertable(session):
    def check_hypertable(table):
        return session.execute(
            text(
                f"""
                SELECT count(*)
                FROM _timescaledb_catalog.hypertable
                WHERE table_name = '{table.__tablename__}'
                """
            )
        ).scalar_one() == 1

    return check_hypertable
