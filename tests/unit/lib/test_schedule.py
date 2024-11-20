from lib.schedule import Lesson, Day, RoomSchedule, Schedule
from datetime import time
import pytest
from pydantic import ValidationError


def create_lesson(
    days: list[Day] = None,
    start: time = None,
    end: time = None,
    name: str = "Example Lesson",
) -> Lesson:
    return Lesson(
        days=days
        or [
            Day.MONDAY,
        ],
        start=start or time(hour=9, minute=0),
        end=end or time(hour=10, minute=0),
        name=name,
    )


def test_lesson__when_start_is_after_end__raises_validation_error():
    with pytest.raises(ValidationError):
        create_lesson(
            start=time(hour=9, minute=30),
            end=time(hour=9, minute=0),
        )


def test_lesson__when_lessons_share_same_time_and_similar_days__returns_true():
    first_lesson = create_lesson(
        days=[Day.MONDAY],
        start=time(hour=9, minute=0),
        end=time(hour=10, minute=0),
    )
    second_lesson = create_lesson(
        days=[Day.MONDAY],
        start=time(hour=9, minute=0),
        end=time(hour=10, minute=0),
    )

    assert first_lesson.overlaps(second_lesson)


def test_lesson__when_lessons_with_different_times_on_the_same_days__returns_false():
    first_lesson = create_lesson(
        days=[Day.MONDAY],
        start=time(hour=8, minute=0),
        end=time(hour=8, minute=45),
    )
    second_lesson = create_lesson(
        days=[Day.MONDAY],
        start=time(hour=9, minute=0),
        end=time(hour=10, minute=0),
    )

    assert not first_lesson.overlaps(second_lesson)


def test_lesson__when_second_lesson_starts_during_first_lesson__overlaps_true():
    first_lesson = create_lesson(
        days=[Day.MONDAY],
        start=time(hour=9, minute=0),
        end=time(hour=9, minute=45),
    )
    second_lesson = create_lesson(
        days=[Day.MONDAY],
        start=time(hour=9, minute=30),
        end=time(hour=10, minute=0),
    )

    assert first_lesson.overlaps(second_lesson)


def create_room_schedule():
    return RoomSchedule(
        name="Room 1",
        lessons=[
            create_lesson(days=[Day.MONDAY], start=time(8, 0), end=time(10, 0)),
            create_lesson(days=[Day.TUESDAY], start=time(8, 0), end=time(10, 0)),
            create_lesson(days=[Day.WEDNESDAY], start=time(8, 0), end=time(10, 0)),
        ],
    )


def test_room_schedule__adding_overlapping_lessons__raises_value_error():
    room = create_room_schedule()
    with pytest.raises(ValueError):
        room.add_lesson(
            create_lesson(days=[Day.WEDNESDAY], start=time(9, 0), end=time(10, 0))
        )


def test_room_schedule__adding_lesson__adds_lesson():
    room = create_room_schedule()
    lesson = create_lesson(days=[Day.THURSDAY], start=time(9, 0), end=time(10, 0))
    room.add_lesson(lesson)
    assert lesson in room.lessons


def test_room_schedule__lessons_by_day__groups_lessons_correctly():
    room = create_room_schedule()
    assert len(room.lessons_by_day[Day.MONDAY]) == 1


def test_room_schedule__removing_lesson__removes_lesson():
    room = create_room_schedule()
    room.remove_lesson(room.lessons[0].id)
    assert len(room.lessons) == 2


def create_schedule():
    return Schedule(
        rooms=[
            create_room_schedule(),
            create_room_schedule(),
        ]
    )


def test_schedule__adding_room_to_schedule__adds_room():
    schedule = create_schedule()
    room = create_room_schedule()
    schedule.add_room(room)
    assert room in schedule.rooms


def test_schedule__adding_same_room_to_schedule__raises_value_error():
    schedule = create_schedule()
    room = create_room_schedule()
    schedule.add_room(room)
    with pytest.raises(ValueError):
        schedule.add_room(room)


def test_schedule__removing_room_from_schedule__removes_room():
    schedule = create_schedule()
    schedule.remove_room(schedule.rooms[0].id)
    assert len(schedule.rooms) == 1
