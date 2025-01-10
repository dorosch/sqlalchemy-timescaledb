import pytest
from sqlalchemy import text

from tests.models import Metric, User


@pytest.mark.asyncio
class TestHypertable:
    async def test_is_hypertable(self, async_session):
        assert (await async_session.execute(
            text(
                f"""
                    SELECT count(*)
                    FROM _timescaledb_catalog.hypertable
                    WHERE table_name = '{Metric.__tablename__}'
                    """
            )
        )).scalar_one()

    async def test_is_not_hypertable(self, async_session):
        assert not (await async_session.execute(
            text(
                f"""
                    SELECT count(*)
                    FROM _timescaledb_catalog.hypertable
                    WHERE table_name = '{User.__tablename__}'
                """
            )
        )).scalar_one()
        #assert False
