import click

from src.models import create_db_models
from src.fetch_data import fetch_all_data


@click.group()
def main():
    """This is the main command."""
    pass


@main.command()
def create_models():
    create_db_models()
    click.echo("Models Created")


@main.command()
def fetch_and_store_data():
    click.echo("Fetching and storing data...")
    fetch_all_data()
    click.echo("Fetched all data")


if __name__ == "__main__":
    main()
