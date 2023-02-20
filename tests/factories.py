import factory
from factory.fuzzy import FuzzyText
from sqlalchemy import orm

from tests.models import Metric

FactorySession = orm.scoped_session(orm.sessionmaker())


class MetricFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Metric
        sqlalchemy_session = FactorySession
        sqlalchemy_session_persistence = 'commit'

    name = FuzzyText()
    value = 0
