from contextlib import contextmanager
from logging import getLogger
import os

import yaml
from lib.schedule import Schedule

logger = getLogger(__name__)


@contextmanager
def schedule_session(
    name: str, data: Schedule | None = None, directory: str | None = None
):
    # use the directory they give us otherwise default to cwd because they don't want to make it in a different dir.
    directory = directory or os.getcwd()
    schedule_path = os.path.join(directory, f"{name}.yaml")

    # save data if we have any for the schedule
    if data is not None:
        with open(schedule_path, "w") as fp:
            # schedules are stored on disk as yaml files.
            yaml.safe_dump(data.model_dump(mode="json"), fp)
    try:
        # just give them a name they can use with the cli
        yield name
    finally:
        # try and delete the schedule file so we don't have to remeber how to every time we run the tests...
        try:
            os.remove(schedule_path)
        except Exception as e:
            # This shouldn't happen unless the schedule was not made either by us or by the tests.
            logger.warning(
                f"Failed to cleanup schedule: {name} at path: {schedule_path}, {e}"
            )
