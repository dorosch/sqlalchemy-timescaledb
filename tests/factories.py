import factory
from factory.fuzzy import FuzzyText

from tests.models import Metric, Session


class MetricFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Metric
        sqlalchemy_session = Session

    name = FuzzyText()
    value = 0
