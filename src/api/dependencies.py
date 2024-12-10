from functools import cache
from lib.schedule import Schedule, RoomSchedule, Lesson, Day
from contextlib import contextmanager
import json

_prefab_schedules: list[Schedule] = [
    Schedule(
        rooms=[
            RoomSchedule(
                name="Room 1",
                lessons=[
                    Lesson(
                        days=[Day.TUESDAY], start="10:00", end="11:00", name="Lesson 1"
                    )
                ],
            )
        ],
    )
]


class ScheduleManager:
    def __init__(self) -> None:
        self._cache: dict[str, Schedule] = {
            str(sched.id): sched for sched in _prefab_schedules
        }

    def get_schedules(self):
        return list(self._cache.values())

    def add_schedule(self, schedule: Schedule):
        self._cache[schedule.id] = schedule

    def get_schedule(self, id: str):
        return self._cache.get(id, None)

    @contextmanager
    def session(self):
        pass


class FileScheduleManager(ScheduleManager):
    def __init__(self) -> None:
        super().__init__()
        self.filename = "schedule.json"
        try:
            with open(self.filename, "r") as fp:
                _cache: dict[str, dict] = json.load(fp)
        except:
            _cache = {}
        self._cache.update(
            {key: Schedule.model_validate(value) for key, value in _cache.items()}
        )

    @contextmanager
    def session(self):
        try:
            yield
        finally:
            try:
                with open(self.filename, "w") as fp:
                    json.dump(
                        {
                            key: value.model_dump(mode="json")
                            for key, value in self._cache.items()
                        },
                        fp,
                    )
            except:
                print("Failed to save changes to disk")


@cache
def schedule_manager():
    return FileScheduleManager()
