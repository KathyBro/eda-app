from datetime import time
from pydantic import BaseModel, Field, model_validator, TypeAdapter
from uuid import uuid4
from enum import Enum


class Day(str, Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class Lesson(BaseModel):
    days: list[Day]
    start: time
    end: time
    name: str
    id: str = Field(default_factory=lambda: str(uuid4()), validate_default=True)

    @model_validator(mode="after")
    def check_overlap(self):
        start = self.start
        end = self.end
        if start and end and start > end:
            raise ValueError("Start time must be before end time.")
        return self

    def overlaps(self, other: "Lesson"):
        return (
            self.start <= other.end
            and self.end >= other.start
            and set(self.days) & set(other.days)
        )


class RoomSchedule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    lessons: list[Lesson] = []

    @property
    def lessons_by_day(self) -> dict[Day, list[Lesson]]:
        return {
            day: [lesson for lesson in self.lessons if day in lesson.days]
            for day in Day
        }

    def add_lesson(self, lesson: Lesson):
        # TODO: Check if the lesson is overlapping
        for existing_lesson in self.lessons:
            if lesson.overlaps(existing_lesson):
                raise ValueError("Lesson overlaps with existing lesson")

        self.lessons.append(lesson)

    def remove_lesson(self, lesson_id: str):
        self.lessons = [lesson for lesson in self.lessons if lesson.id != lesson_id]


"""
    schedule = RoomSchedule(
        name="Room 1",
        lessons=[
            Lesson(days=[Day.MONDAY], start=datetime(2023, 1, 1, 8, 0), end=datetime(2023, 1, 1, 10, 0)),
            Lesson(days=[Day.TUESDAY], start=datetime(2023, 1, 1, 8, 0), end=datetime(2023, 1, 1, 10, 0)),
            Lesson(days=[Day.WEDNESDAY], start=datetime(2023, 1, 1, 8, 0), end=datetime(2023, 1, 1, 10, 0)),
        )
    )
"""


class Schedule(BaseModel):
    rooms: list[RoomSchedule]

    def add_room(self, room: RoomSchedule):
        for existing_room in self.rooms:
            if existing_room.id == room.id:
                raise ValueError("Room already exists")
        self.rooms.append(room)

    def remove_room(self, room_id: str):
        self.rooms = [room for room in self.rooms if room.id != room_id]
