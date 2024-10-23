import pytest
from sqlalchemy import create_engine, text

from sqlalchemy.orm import Session

from tests.factories import FactorySession
from tests.models import Base, DATABASE_URL


@pytest.fixture
def psycopg_engine():
    yield create_engine(
        DATABASE_URL.set(drivername='timescaledb+psycopg')
    )

@pytest.fixture
def session(psycopg_engine):
    with Session(psycopg_engine) as session:
        yield session


@pytest.fixture(autouse=True)
def setup(psycopg_engine):
    FactorySession.configure(bind=psycopg_engine)
    Base.metadata.create_all(bind=psycopg_engine)
    yield
    Base.metadata.drop_all(bind=psycopg_engine)


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
