import click


@click.group()
def main():
    """
    CLI that allows you to edit a global schedule files and view them.
    """
    pass


@main.group()
def schedule():
    """
    Commands related to schedule management
    """
    pass
