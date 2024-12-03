import shutil
import os
import pytest

from click.testing import CliRunner
import yaml
from cli.app import main
from lib.schedule import Schedule
from tests.integration.cli.utils import schedule_session


@pytest.fixture
def schedule():
    data = Schedule(
        rooms=[],
    )
    with schedule_session("My CLI Test Schedule", data=data) as schedule_name:
        yield schedule_name


# *********** EDIT SCHEDULE TESTS **************
# ******* ADD ROOM TESTS *******
def test_edit_schedule_create_room_space_for_room_name_fails(
    schedule,
):
    runner = CliRunner()
    result = runner.invoke(main, ["schedule", "edit", schedule, "create-room", " "])
    assert result.exit_code == 1


def test_edit_schedule_create_room_no_room_name_fails(
    schedule,
):
    runner = CliRunner()
    result = runner.invoke(main, ["schedule", "edit", schedule, "create-room", ""])
    assert result.exit_code == 1


def test_edit_schedule_create_room_duplicate_file_name_succeeds(
    schedule,
):
    runner = CliRunner()
    room_name = "My CLI Test Room"
    result = runner.invoke(
        main,
        ["schedule", "edit", schedule, "create-room", room_name],
    )
    result = runner.invoke(
        main,
        ["schedule", "edit", schedule, "create-room", room_name],
    )
    assert result.exit_code == 0


def test_edit_schedule_create_room_succeeds(schedule, room):
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["schedule", "edit", schedule, "create-room", "My CLI Test Room"],
    )
    assert result.exit_code == 0


# ******* REMOVE ROOM TESTS *******
def test_edit_schedule_remove_room_space_for_room_name_succeeds(
    schedule,
):
    runner = CliRunner()
    # Remove a room that was never created
    result = runner.invoke(
        main,
        ["schedule", "edit", schedule, "remove-room", "Nonexistant Room"],
    )
    assert result.exit_code == 0


def test_edit_schedule_remove_room_succeeds(
    schedule,
):
    runner = CliRunner()
    # Create the room
    result = runner.invoke(
        main,
        ["schedule", "edit", schedule, "create-room", "My CLI Test Room"],
    )
    # Remove the room
    result = runner.invoke(
        main,
        ["schedule", "edit", schedule, "remove-room", "My CLI Test Room"],
    )
    assert result.exit_code == 0
    # Check if room is still there, aka view nonexistant room
    result = runner.invoke(
        main, ["schedule", "view", schedule, "room", "My CLI Test Room"]
    )
    assert "does not exist." in result.output


@pytest.fixture
def room(schedule):
    runner = CliRunner()
    room_name = "My CLI Test Room"
    runner.invoke(
        main,
        ["schedule", "edit", schedule, "create-room", room_name],
    )
    return room_name


def test_edit_schedule_add_lesson_missing_required_day_option_fails(
    schedule,
    room,
):
    runner = CliRunner()
    # Create the room

    # Add Lesson
    result = runner.invoke(
        main,
        [
            "schedule",
            "edit",
            schedule,
            "room",
            room,
            "add-lesson",
            "-s",
            "10:00",
            "-e",
            "11:00",
            "-n",
            "My CLI Test Lesson",
        ],
    )
    assert result.exit_code == 2


def test_edit_schedule_add_lesson_missing_required_start_time_option_fails(
    schedule,
    room,
):
    runner = CliRunner()
    # Add Lesson
    result = runner.invoke(
        main,
        [
            "schedule",
            "edit",
            schedule,
            "room",
            room,
            "add-lesson",
            "-d",
            "monday",
            "-e",
            "11:00",
            "-n",
            "My CLI Test Lesson",
        ],
    )
    assert result.exit_code == 2


def test_edit_schedule_add_lesson_missing_required_end_time_option_fails(
    schedule,
    room,
):
    runner = CliRunner()
    # Add Lesson
    result = runner.invoke(
        main,
        [
            "schedule",
            "edit",
            schedule,
            "room",
            room,
            "add-lesson",
            "-d",
            "monday",
            "-s",
            "10:00",
            "-n",
            "My CLI Test Lesson",
        ],
    )
    # Remove Schedule
    current_dir = os.getcwd()
    os.remove(os.path.join(current_dir, "My CLI Test Schedule.yaml"))
    assert result.exit_code == 2


def test_edit_schedule_add_lesson_missing_required_name_option_fails(
    schedule,
    room,
):
    runner = CliRunner()
    # Add Lesson
    result = runner.invoke(
        main,
        [
            "schedule",
            "edit",
            schedule,
            "room",
            room,
            "add-lesson",
            "-d",
            "monday",
            "-s",
            "10:00",
            "-e",
            "11:00",
        ],
    )
    # Remove Schedule
    current_dir = os.getcwd()
    os.remove(os.path.join(current_dir, "My CLI Test Schedule.yaml"))
    assert result.exit_code == 2


@pytest.mark.parametrize(
    "days, start_time, end_time, name, exit_code",
    [
        (["monday"], "10:00", "11:00", "Monday Madness", 0),
        (["tuesday"], "10:00", "11:00", "Taco Tuesday with President Business", 0),
        (["wednesday"], "10:00", "11:00", "Wednesday's Child Full Of Woe", 0),
        (["thursday"], "10:00", "11:00", "Thursday Tennis", 0),
        (["friday"], "10:00", "11:00", "Friday Night Lights", 0),
        (["saturday"], "10:00", "11:00", "Saturday Sadness Sad-agement", 0),
        (["sunday"], "10:00", "11:00", "Sunday Social", 0),
        (
            ["thursday", "tuesday"],
            "10:00",
            "11:00",
            "Tuesday, Thursday Tennis Jamboree",
            0,
        ),
        (["MONDAY"], "10:00", "11:00", "Invalid Day Test", 2),
        (["thursday"], "12:00", "11:00", "Start After End Time", 1),
        (["thursday"], "32:00", "11:00", "Start Time That Isn't Possible", 2),
        (["thursday"], "10:00", "48:00", "End Time Isn't Possible", 2),
    ],
)
def test_edit_schedule_add_lesson__when_given_inputs__gets_expected_exit_code(
    schedule, room, days, start_time, end_time, name, exit_code
):
    runner = CliRunner()
    formatted_days = []
    for day in days:
        formatted_days.append("-d")
        formatted_days.append(day)

    result = runner.invoke(
        main,
        [
            "schedule",
            "edit",
            schedule,
            "room",
            room,
            "add-lesson",
            *formatted_days,
            "-s",
            start_time,
            "-e",
            end_time,
            "-n",
            name,
        ],
    )
    assert result.exit_code == exit_code


def test_edit_schedule_add_lesson_duplicate_lesson_fails(schedule, room):
    runner = CliRunner()

    # Create the room
    runner.invoke(
        main,
        [
            "schedule",
            "edit",
            schedule,
            "create-room",
            "My CLI Test Room",
        ],
    )
    # Add Lesson
    result = runner.invoke(
        main,
        [
            "schedule",
            "edit",
            schedule,
            "room",
            "My CLI Test Room",
            "add-lesson",
            "-d",
            "monday",
            "-s",
            "10:00",
            "-e",
            "11:00",
            "-n",
            "My CLI Test Lesson",
        ],
    )
    result = runner.invoke(
        main,
        [
            "schedule",
            "edit",
            schedule,
            "room",
            "My CLI Test Room",
            "add-lesson",
            "-d",
            "monday",
            "-s",
            "10:00",
            "-e",
            "11:00",
            "-n",
            "My CLI Test Lesson",
        ],
    )
    # Remove Schedule
    current_dir = os.getcwd()
    os.remove(os.path.join(current_dir, "My CLI Test Schedule.yaml"))
    assert result.exit_code == 1


# ******* REMOVE LESSON TESTS *******
def test_edit_schedule_remove_lesson_succeeds(schedule, room):
    runner = CliRunner()
    lesson_name = "My CLI Test Lesson"
    runner.invoke(
        main,
        [
            "schedule",
            "edit",
            schedule,
            "room",
            room,
            "add-lesson",
            "-d",
            "monday",
            "-s",
            "10:00",
            "-e",
            "11:00",
            "-n",
            lesson_name,
        ],
    )
    # Remove Lesson
    result = runner.invoke(
        main,
        [
            "schedule",
            "edit",
            schedule,
            "room",
            room,
            "remove-lesson",
            lesson_name,
        ],
    )
    current_dir = os.getcwd()

    # Check Lesson Was Removed

    with open(os.path.join(current_dir, f"{schedule}.yaml"), "r") as f:
        schedule_dict = yaml.safe_load(f)

    assert schedule_dict["rooms"][0]["lessons"] == [], "Lesson was not removed"
    assert result.exit_code == 0


def test_edit_schedule_remove_lesson_does_not_exist_succeeds(schedule, room):
    runner = CliRunner()

    # Create the room
    runner.invoke(
        main,
        [
            "schedule",
            "edit",
            schedule,
            "create-room",
            "My CLI Test Room",
        ],
    )
    # Remove Lesson
    result = runner.invoke(
        main,
        [
            "schedule",
            "edit",
            schedule,
            "room",
            "My CLI Test Room",
            "remove-lesson",
            "My CLI Test Lesson",
        ],
    )
    # Remove Schedule
    current_dir = os.getcwd()
    os.remove(os.path.join(current_dir, "My CLI Test Schedule.yaml"))
    assert result.exit_code == 0


@pytest.fixture
def lesson(schedule, room):
    runner = CliRunner()
    lesson_name = "My CLI Test Lesson"
    runner.invoke(
        main,
        [
            "schedule",
            "edit",
            schedule,
            "room",
            room,
            "add-lesson",
            "-d",
            "monday",
            "-s",
            "10:00",
            "-e",
            "11:00",
            "-n",
            lesson_name,
        ],
    )
    return lesson_name


# ******* EDIT LESSON TESTS *******
def test_edit_schedule_edit_lesson_lesson_doesnt_exist_fails(schedule, room):
    runner = CliRunner()
    # Edit Lesson
    result = runner.invoke(
        main,
        [
            "schedule",
            "edit",
            schedule,
            "room",
            room,
            "edit-lesson",
            "DNE",
            "-d",
            "monday",
        ],
    )
    assert result.exit_code == 2


def test_edit_schedule_edit_lesson_change_day_succeeds(schedule, room, lesson):
    runner = CliRunner()
    # Edit Lesson
    result = runner.invoke(
        main,
        [
            "schedule",
            "edit",
            schedule,
            "room",
            room,
            "lesson",
            lesson,
            "-d",
            "tuesday",
        ],
    )
    # Check Lesson Contains New Day
    current_dir = os.getcwd()
    with open(os.path.join(current_dir, "My CLI Test Schedule.yaml"), "r") as f:
        schedule_dict = yaml.safe_load(f)
        assert schedule_dict["rooms"][0]["lessons"][0]["days"] == ["tuesday"]
    # Remove Schedule
    assert result.exit_code == 0


def test_edit_schedule_edit_lesson_add_day_succeeds(schedule, room, lesson):
    runner = CliRunner()
    # Edit Lesson
    result = runner.invoke(
        main,
        [
            "schedule",
            "edit",
            schedule,
            "room",
            room,
            "lesson",
            lesson,
            "-d",
            "monday",
            "-d",
            "tuesday",
            "-d",
            "thursday",
        ],
    )
    # Check Lesson Contains New Day
    current_dir = os.getcwd()
    with open(os.path.join(current_dir, "My CLI Test Schedule.yaml"), "r") as f:
        schedule_dict = yaml.safe_load(f)
        assert schedule_dict["rooms"][0]["lessons"][0]["days"] == [
            "monday",
            "tuesday",
            "thursday",
        ]
    # Remove Schedule
    os.remove(os.path.join(current_dir, "My CLI Test Schedule.yaml"))
    assert result.exit_code == 0


def test_edit_schedule_edit_lesson_start_time_after_end_time_fails(
    schedule, room, lesson
):
    runner = CliRunner()
    # end_time is 11:00
    # Edit Lesson
    result = runner.invoke(
        main,
        [
            "schedule",
            "edit",
            schedule,
            "room",
            room,
            "lesson",
            lesson,
            "-d",
            "monday",
            "-s",
            "11:10",
        ],
    )
    assert result.exit_code == 1, result.output
    assert "Start time must be before end time" in result.output


def test_edit_schedule_edit_lesson_end_time_before_start_time_fails(
    schedule, room, lesson
):
    runner = CliRunner()
    # Edit Lesson
    result = runner.invoke(
        main,
        [
            "schedule",
            "edit",
            schedule,
            "room",
            room,
            "lesson",
            lesson,
            "-e",
            "06:00",
        ],
    )
    assert result.exit_code == 1, result.output
    assert "End time must be after start time" in result.output


def test_edit_schedule_edit_lesson_start_time_and_end_time_are_the_same_fails(
    schedule, room, lesson
):
    runner = CliRunner()
    # Edit Lesson
    result = runner.invoke(
        main,
        [
            "schedule",
            "edit",
            schedule,
            "room",
            room,
            "lesson",
            lesson,
            "-s",
            "10:00",
            "-e",
            "10:00",
        ],
    )
    assert result.exit_code == 1, result.output
    assert "Start and end times must be different" in result.output


def test_edit_schedule_change_to_valid_start_time_succeeds(schedule, room, lesson):
    runner = CliRunner()
    # Edit Lesson
    result = runner.invoke(
        main,
        [
            "schedule",
            "edit",
            schedule,
            "room",
            room,
            "lesson",
            lesson,
            "-s",
            "08:00",
        ],
    )
    assert result.exit_code == 0


def test_edit_schedule_change_to_valid_end_time_succeeds(schedule, room, lesson):
    runner = CliRunner()
    # Edit Lesson
    result = runner.invoke(
        main,
        [
            "schedule",
            "edit",
            schedule,
            "room",
            room,
            "lesson",
            lesson,
            "-e",
            "13:00",
        ],
    )
    assert result.exit_code == 0


def test_edit_schedule_change_to_valid_name_succeeds(schedule, room, lesson):
    runner = CliRunner()
    # Edit Lesson
    result = runner.invoke(
        main,
        [
            "schedule",
            "edit",
            schedule,
            "room",
            room,
            "lesson",
            lesson,
            "-n",
            "New Name",
        ],
    )
    assert result.exit_code == 0
