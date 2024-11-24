"""
    CLI that allows you to edit a global schedule file.
    
    Usage:
    
    ```bash
    > eda-app schedule create "My Schedule" -d /path/to/save-files/
    # Creates schedule and saves it to yaml file

    > eda-app schedule edit "My Schedule" create-room "My First Room"
    # Adds a room called My First Room

    > eda-app schedule edit "My Schedule" remove-room "My First Room"
    # Removes a room called My First Room
    
    > eda-app schedule edit "My Schedule" room "My First Room" add-lesson -d monday -d tuesday -d thrusday -s 10:00 -e 11:00 -n "My First Lesson"
    # Adds a lesson to the My First Room called My First Lesson

    > eda-app schedule edit "My Schedule" room "My First Room" remove-lesson "My First Lesson"
    # Removes a lesson called My First Lesson

    > eda-app schedule edit "My Schedule" room "My First Room" lesson "First Lesson" [Options]
    # Edits a specific lesson of a room based on the options passed in
    
    > eda-app schedule view "My Schedule"
    # Prints out the schedule to the screen in a human readable format
    
    > eda-app schedule view "My Schedule" room "My First Room"
    # Prints out the schedule for a room in a human readable format
    ```
"""

from .app import main
import cli.create  # noqa  registers the commands to create schedules
import cli.edit  # noqa  registers the commands to edit schedules
import cli.view  # noqa  registers the commands to view schedules

__all__ = [
    "main",
    "create",
    "edit",
    "view",
]
