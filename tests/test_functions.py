from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy_timescaledb.functions import First, Last

from tests.models import Metric


class TestFirstFunction:
    def setup_class(self):
        self.today = datetime.now()
        self.three_days_ago = self.today - timedelta(days=3)
        self.six_days_ago = self.today - timedelta(days=6)
        self.query = select(
            First(Metric.value, Metric.timestamp)
        ).select_from(Metric)

    def test_first_record_without_data(self, session):
        assert session.execute(self.query).scalar_one_or_none() is None

    def test_first_record_with_one_record(self, session, metric_factory):
        metric_factory(timestamp=self.today, value=1)

        assert session.execute(self.query).scalar_one_or_none()

    def test_first_record_with_multiple_records(self, session, metric_factory):
        metric_factory(timestamp=self.today)
        metric_factory(timestamp=self.three_days_ago)
        metric_factory(timestamp=self.six_days_ago, value=1)

        assert session.execute(self.query).scalar_one()

    def test_first_record_with_group_by(self, session, metric_factory):
        metric_factory(name='test', timestamp=self.today)
        metric_factory(name='test', timestamp=self.three_days_ago)
        metric_factory(name='test', timestamp=self.six_days_ago, value=1)

        assert session.execute(self.query.group_by(Metric.name)).scalar_one()


class TestLastFunction:
    def setup_class(self):
        self.today = datetime.now()
        self.three_days_ago = self.today - timedelta(days=3)
        self.six_days_ago = self.today - timedelta(days=6)
        self.query = select(
            Last(Metric.value, Metric.timestamp)
        ).select_from(Metric)

    def test_last_record_without_data(self, session):
        assert session.execute(self.query).scalar_one_or_none() is None

    def test_last_record_with_one_record(self, session, metric_factory):
        metric_factory(timestamp=self.today, value=1)

        assert session.execute(self.query).scalar_one_or_none()

    def test_last_record_with_multiple_records(self, session, metric_factory):
        metric_factory(timestamp=self.today, value=1)
        metric_factory(timestamp=self.three_days_ago)
        metric_factory(timestamp=self.six_days_ago)

        assert session.execute(self.query).scalar_one()

    def test_last_record_with_group_by(self, session, metric_factory):
        metric_factory(name='test', timestamp=self.today, value=1)
        metric_factory(name='test', timestamp=self.three_days_ago)
        metric_factory(name='test', timestamp=self.six_days_ago)

        assert session.execute(self.query.group_by(Metric.name)).scalar_one()
