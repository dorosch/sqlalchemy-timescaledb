import pytest
from pytest_factoryboy import register
from sqlalchemy import text, create_engine
from sqlalchemy.orm import Session

from tests.factories import MetricFactory, FactorySession
from tests.models import Base, DATABASE_URL

register(MetricFactory)


@pytest.fixture
def engine():
    yield create_engine(DATABASE_URL, echo=True)


@pytest.fixture
def session(engine):
    with Session(engine) as session:
        yield session


_factory_session = None

@pytest.fixture(autouse=True)
def setup(engine):
    global _factory_session
    if _factory_session is None:
        _factory_session = FactorySession.configure(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


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
