import os

from alembic import command
from alembic.config import Config

from tests.models import Base, engine


class TestAlembic:
    def setup_class(self):
        self.config = Config(
            os.path.join(os.path.dirname(__file__), 'alembic.ini')
        )

    def test_create_revision(self):
        Base.metadata.drop_all(bind=engine)
        script = command.revision(self.config, autogenerate=True)
        Base.metadata.create_all(bind=engine)

        assert script.down_revision is None
