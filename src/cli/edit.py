from datetime import datetime
import os
import click
import yaml

from lib.schedule import Day, Lesson, RoomSchedule, Schedule
from .app import schedule


@schedule.group("edit")
@click.argument("name", type=click.STRING)
@click.option(
    "-d",
    "--directory",
    type=click.Path(
        dir_okay=True,
        file_okay=False,
        exists=True,
        writable=True,
    ),
    help="Directory schedule was saved to.",
    default=os.getcwd(),
)
@click.pass_context
def edit_schedule(ctx: click.Context, name: str, directory: str | None):
    """
    Commands related to editing a schedule
    """
    directory = directory or os.getcwd()
    path = os.path.join(directory, f"{name}.yaml")
    if not os.path.exists(path):
        raise click.ClickException(f"Schedule with name {name!r} does not exist.")

    with open(path, "r") as f:
        schedule_dict = yaml.safe_load(f)
    ctx.obj = {
        "schedule": Schedule.model_validate(schedule_dict),
    }

    @ctx.call_on_close
    def save_schedule():
        with open(path, "w") as f:
            schedule_dict = ctx.obj["schedule"].model_dump(mode="json")
            print("Saving schedule...")
            yaml.safe_dump(schedule_dict, f)


@edit_schedule.command(
    "create-room"
)  # python -m cli schedule edit "Schedule Name" create-room "Room Name"
@click.argument("name", type=click.STRING)
@click.pass_context
def add_room(ctx: click.Context, name: str):
    """
    Adds a room to the schedule
    """
    _schedule: Schedule = ctx.obj.get("schedule")

    if name.strip() == "":
        raise click.ClickException(
            "Schedule name cannot be empty or only contain spaces."
        )

    room = RoomSchedule(name=name)
    try:
        _schedule.add_room(room)
    except ValueError as err:
        raise click.ClickException(err)


@edit_schedule.command(
    "remove-room"
)  # python -m cli schedule edit "Schedule Name" remove-room "Room Name"
@click.argument("room_name", type=click.STRING)
@click.pass_context
def remove_room(ctx: click.Context, room_name: str):
    """
    Removes a room from the schedule
    """
    _schedule: Schedule = ctx.obj.get("schedule")
    room_id = None
    for room in _schedule.rooms:
        if room.name == room_name:
            room_id = room.id
            break

    if room_id is None:
        click.echo(f"Room with name {room_name!r} does not exist.")
        return

    try:
        _schedule.remove_room(room_id)
        click.echo("Room removed successfully.")
    except ValueError as err:
        raise click.ClickException(err)


@edit_schedule.group(
    "room"
)  # python -m cli schedule edit "Schedule Name" room "Room Name" [OPTIONS]
@click.argument("room_name", type=click.STRING)
@click.pass_context
def room_group(ctx: click.Context, room_name: str):
    """
    Commands related to editing a room
    """
    existing_room = None
    _schedule = ctx.obj.get("schedule")
    for room in _schedule.rooms:
        if room.name == room_name:
            existing_room = room
            break
    if existing_room is None:
        raise click.ClickException(f"Room with name {room_name!r} does not exist.")

    ctx.obj["room"] = existing_room


@room_group.command(
    "add-lesson"
)  # python -m cli schedule edit "Schedule Name" room "Room Name" add-lesson [OPTIONS]
@click.option("-d", "--days", multiple=True, type=click.Choice(Day), required=True)
@click.option("-s", "--start", type=click.DateTime(["%H:%M"]), required=True)
@click.option("-e", "--end", type=click.DateTime(["%H:%M"]), required=True)
@click.option("-n", "--name", type=click.STRING, required=True)
@click.pass_context
def add_lesson(
    ctx: click.Context, days: list[Day], start: datetime, end: datetime, name: str
):
    """
    Adds a lesson to the room
    """
    # TODO(Kathy): Add checking for if there is multiple lessons of the same name, that we remove the correct lesson
    room = ctx.obj.get("room")
    try:
        room.add_lesson(
            Lesson(days=days, start=start.time(), end=end.time(), name=name)
        )
        click.echo("Lesson added successfully.")
    except ValueError as err:
        raise click.ClickException(err)


@room_group.command(
    "remove-lesson"
)  # python -m cli schedule edit "Schedule Name" room "Room Name" remove-lesson "Lesson Name"
@click.argument("lesson_name", type=click.STRING)
@click.pass_context
def remove_lesson(ctx: click.Context, lesson_name: str):
    """
    Removes a lesson from the room
    """
    room: RoomSchedule = ctx.obj.get("room")
    lesson_id = None
    for lesson in room.lessons:
        if lesson.name == lesson_name:
            lesson_id = lesson.id
            break

    if lesson_id is None:
        click.echo(f"Lesson with name {lesson_name!r} does not exist.")
        return

    try:
        room.remove_lesson(lesson_id)
        click.echo("Lesson removed successfully.")
    except ValueError as err:
        raise click.ClickException(err)


@room_group.command(
    "lesson"
)  # python -m cli schedule edit "Schedule Name" room "Room Name" lesson "Lesson Name"
@click.argument("lesson_name", type=click.STRING)
@click.option("-d", "--days", multiple=True, type=click.Choice(Day))
@click.option("-s", "--start", type=click.DateTime(["%H:%M"]))
@click.option("-e", "--end", type=click.DateTime(["%H:%M"]))
@click.option("-n", "--name", type=click.STRING)
@click.pass_context
def edit_lesson(
    ctx: click.Context,
    lesson_name: str,
    days: list[Day] = [],
    start: datetime = None,
    end: datetime = None,
    name: str = None,
):
    """
    Commands related to editing a lesson
    """
    existing_lesson = None
    room: RoomSchedule = ctx.obj.get("room")
    for lesson in room.lessons:
        if lesson.name == lesson_name:
            existing_lesson = lesson
            break
    if existing_lesson is None:
        raise click.ClickException(f"Lesson with name {lesson_name!r} does not exist.")
    if days:
        existing_lesson.days = [day for day in days]
    if name:
        existing_lesson.name = name
    start = None if start is None else start.time()
    end = None if end is None else end.time()
    if start and end:
        if start > end:
            raise click.ClickException(f"Start time must be before end time.")
        elif start == end:
            raise click.ClickException("Start and end times must be different.")
        existing_lesson.start = start
        existing_lesson.end = end
    elif start:
        if start > existing_lesson.end:
            raise click.ClickException(f"Start time must be before end time.")
        existing_lesson.start = start
    elif end:
        if end < existing_lesson.start:
            raise click.ClickException("End time must be after start time.")
        existing_lesson.end = end
