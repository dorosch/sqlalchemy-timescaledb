from sqlalchemy import text

from tests.models import Metric


class TestHypertable:
    def test_is_it_hypertable(self, session):
        assert session.execute(text(
            f"""
            SELECT count(*)
            FROM _timescaledb_catalog.hypertable
            WHERE table_name = '{Metric.__tablename__}'
            """
        )).scalar_one()
