import os
import click
import tabulate
import yaml

from lib.schedule import Schedule, RoomSchedule
from .app import schedule


@schedule.group("view", invoke_without_command=True)
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
def view_schedule(
    ctx: click.Context,
    name: str,
    directory: str,
):
    """
    Command relating to viewing the schedule
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
    if ctx.invoked_subcommand is None:
        click.echo(tabulate_schedule(ctx.obj["schedule"]))


def tabulate_schedule(schedule: Schedule):
    table_schedules = [
        f"{' ' * 25}{room.name}({room.id})\n{tabulate_room_schedule(room)}"
        for room in schedule.rooms
    ]
    return "\n********************************\n".join(table_schedules)


@view_schedule.command("room")
@click.argument("room_name", type=click.STRING)
@click.pass_context
def view_room(ctx: click.Context, room_name: str):
    _schedule: Schedule = ctx.obj.get("schedule")
    room = None
    for _room in _schedule.rooms:
        if _room.name == room_name:
            room = _room
            break

    if room is None:
        click.echo(f"Room with name {room_name!r} does not exist.")
        return

    click.echo(tabulate_room_schedule(room))


def tabulate_room_schedule(room: RoomSchedule):

    return tabulate.tabulate(
        [
            [
                lesson.id,
                lesson.name,
                ", ".join(lesson.days),
                lesson.start.strftime("%H:%M"),
                lesson.end.strftime("%H:%M"),
            ]
            for lesson in room.lessons
        ],
        headers=[
            "id",
            "name",
            "days",
            "start",
            "end",
        ],
        tablefmt="rounded_grid",
        # maxcolwidths=[20, 10, 20, 8, 8],
    )
