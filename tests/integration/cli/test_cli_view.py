from click.testing import CliRunner
from cli.app import main
import pytest
from tests.integration.cli.utils import schedule_session
from lib.schedule import Schedule, RoomSchedule, Lesson, Day


# ********** VIEW SCHEDULE TESTS **********
def test_view_schedule_succeeds():
    runner = CliRunner()
    schedule = Schedule(
        rooms=[
            RoomSchedule(
                name="Homeroom",
                lessons=[
                    Lesson(
                        days=[Day.MONDAY],
                        start="09:00",
                        end="10:00",
                        name="My First Lesson",
                    )
                ],
            )
        ]
    )
    with schedule_session("Valid", data=schedule) as name:
        result = runner.invoke(main, ["schedule", "view", name])
    assert result.exit_code == 0
    assert "My First Lesson" in result.output
    assert "Homeroom" in result.output


def test_view_schedule_noexistant_schedule_fails():
    runner = CliRunner()
    result = runner.invoke(main, ["schedule", "view", "Nonexistant Schedule"])
    assert result.exit_code == 1
    assert "does not exist" in result.output


# ********** VIEW ROOM TESTS **********
def test_view_room_with_lesson_succeeds():
    runner = CliRunner()
    room_name = "Homeroom"
    schedule = Schedule(
        rooms=[
            RoomSchedule(
                name=room_name,
                lessons=[
                    Lesson(
                        days=[Day.MONDAY],
                        start="09:00",
                        end="10:00",
                        name="My First Lesson",
                    )
                ],
            )
        ]
    )
    with schedule_session("Valid", data=schedule) as name:
        result = runner.invoke(main, ["schedule", "view", name, "room", room_name])
    assert result.exit_code == 0
    assert "My First Lesson" in result.output


def test_view_room_noexistant_room_fails():
    runner = CliRunner()
    result = runner.invoke(
        main, ["schedule", "view", "Nonexistant Schedule", "room", "Nonexistant Room"]
    )
    assert result.exit_code == 1


def test_view_room_with_no_lessons_succeeds():
    runner = CliRunner()
    room_name = "Homeroom"
    schedule = Schedule(
        rooms=[
            RoomSchedule(
                name=room_name,
                lessons=[],
            )
        ]
    )
    with schedule_session("Valid", data=schedule) as name:
        result = runner.invoke(main, ["schedule", "view", name, "room", room_name])
    assert result.exit_code == 0
