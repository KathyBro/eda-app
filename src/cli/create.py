import os
import click
import yaml

from lib.schedule import Schedule
from .app import schedule


@schedule.command("create")  # python -m cli schedule view "Name" -d "path/to/dir"
@click.argument(
    "name",
    type=click.STRING,
)
@click.option(
    "-d",
    "--directory",
    type=click.Path(
        dir_okay=True,
        file_okay=False,
        exists=True,
        writable=True,
    ),
    help="Directory to save schedule to.",
)
def create_schedule(
    name: str,
    directory: str | None,
):
    """
    Create a new schedule and saves it to the file.
    """
    directory = directory or os.getcwd()
    path = os.path.join(directory, f"{name}.yaml")
    if os.path.exists(path):
        raise click.ClickException(f"Schedule with name {name!r} already exists.")
    if name.strip() == "":
        raise click.ClickException(
            "Schedule name cannot be empty or only contain spaces."
        )

    with open(path, "w") as f:
        schedule_instance = Schedule(rooms=[])
        schedule_dict = schedule_instance.model_dump(mode="json")
        yaml.safe_dump(schedule_dict, f)
