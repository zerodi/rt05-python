import click
import toml
from teplocom.client import TeplocomClient


def get_client():
    config = toml.load('config.toml')
    connect_config = config['SERIAL']
    slave_id = config['DEVICE']['slave_id']

    return TeplocomClient(connect_config, slave_id)


@click.group()
def cli():
    pass

@cli.command()
def ping():
    client = get_client()
    client.ping()


@cli.command()
def current():
    client = get_client()
    client.current()


if __name__ == '__main__':
    cli()
