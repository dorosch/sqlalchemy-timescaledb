from tests.models import Metric, User


class TestHypertable:
    def test_is_hypertable(self, is_hypertable):
        assert is_hypertable(Metric)

    def test_is_not_hypertable(self, is_hypertable):
        assert not is_hypertable(User)
