from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from collections import defaultdict
from lib.schedule import Day


class NewLesson(BaseModel):
    days: list[Day]
    start: str
    end: str
    name: str

    def validate(self):
        if len(set(self.days)) != len(self.days):
            raise ValueError("Cannot use the same day twice")
        if self.start >= self.end:
            raise ValueError("Cannot have start time at or after end time.")
        if self.name.strip() == "":
            raise ValueError("Must supply a name to the lesson.")

    def overlaps(self, other: "NewLesson"):
        return (
            self.start <= other.end
            and self.end >= other.start
            and set(self.days) & set(other.days)
        )


class UpdateLesson(BaseModel):
    days: Optional[list[Day]] = None
    start: Optional[str] = None
    end: Optional[str] = None
    name: Optional[str] = None

    def validate(self):
        if self.start is not None and self.end is not None and self.start >= self.end:
            raise ValueError("Cannot have start time at or after end time.")
        if self.days is not None:
            if len(set(self.days)) != len(self.days):
                raise ValueError("Cannot use the same day twice")
        if self.name is not None and self.name.strip() == "":
            raise ValueError("Must supply a name to the lesson.")

    def overlaps(self, other: "UpdateLesson"):
        return (
            self.start <= other.end
            and self.end >= other.start
            and set(self.days) & set(other.days)
        )


class NewRoom(BaseModel):
    name: str
    lessons: list[NewLesson] = []

    def validate(self):
        if self.name.strip() == "":
            raise ValueError("Name must be given")
        for lesson in self.lessons:
            lesson.validate()

        for index, lesson in enumerate(self.lessons):
            for other_lesson in self.lessons[index + 1 :]:
                if lesson.overlaps(other_lesson):
                    raise ValueError("Lessons cannot overlap")


class UpdateRoom(BaseModel):
    name: Optional[str] = None
    lessons: Optional[list[NewLesson]] = None

    def validate(self):
        if self.name is not None and self.name.strip() == "":
            raise ValueError("Name must be given")
        if self.lessons is not None:
            for lesson in self.lessons:
                lesson.validate()

            for index, lesson in enumerate(self.lessons):
                for other_lesson in self.lessons[index + 1 :]:
                    if lesson.overlaps(other_lesson):
                        raise ValueError("Lessons cannot overlap")


class NewSchedule(BaseModel):
    rooms: list[NewRoom] = []

    def validate(self):
        instance = defaultdict(list)
        for room in self.rooms:
            instance[room.name].append(room)

        if any(len(rooms) > 1 for rooms in instance):
            raise ValueError("Cannot have rooms that share the same name!!")

        for room in self.rooms:
            room.validate()
