import pytest
from logging import getLogger

from tests.integration.cli.utils import schedule_session

logger = getLogger(__name__)


@pytest.fixture
def default_schedule_in_current_dir():
    name = "Schedule"
    with schedule_session(name) as session_name:
        yield session_name
