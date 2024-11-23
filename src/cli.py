import click


@click.command()
def main():
    print("Hello, World!")


@click.command()
@click.option("--count", default=1, help="Number of greetings.")
@click.option("--name", prompt="Your name", help="The person to greet.")
def hello(count, name):
    for x in range(count):
        click.echo("Hello %s!" % name)


@click.command()
@click.option()
def create_lesson(days, start, end, name):
    pass


if __name__ == "__main__":  # pragma: no cover
    main()
