import click

from src.models import create_db_models
from src.fetch_data import fetch_all_data
from src.stats import BuildAccountDelegation, VoteStatBuilder, GenerateDistribution

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


@main.command()
def generate_distribution():
    click.echo("Building delegation records...")
    BuildAccountDelegation().build()
    click.echo("delegation records built")
    click.echo("Building vote stats...")
    VoteStatBuilder().build()
    click.echo("Built vote stats")
    click.echo("Generating distribution...")
    GenerateDistribution().generate()
    click.echo("generated distribution")


if __name__ == "__main__":
    main()
