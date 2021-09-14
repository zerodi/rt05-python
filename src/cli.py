import functools
from typing import Callable

import click

from client import get_client
from server import run_server


def common_params(func: Callable) -> Callable:
    @click.option('-c', '--config', type=str, help='Path to config.toml file')
    @click.option('--port', type=str, help='Device port')
    @click.option('--baudrate', type=int, default=9600, help='Baudrate of connection')
    @click.option('--parity', type=str, default='N', help='Parity of connection')
    @click.option('--bytesize', type=int, default=8, help='Bytesize of connection')
    @click.option('--stopbits', type=int, default=1, help='Stop bits of connection')
    @click.option('--slave-id', type=int, default=1, help='Device Id in Serial network')
    @functools.wraps(func)
    def wrapper(**kwargs: dict) -> Callable:
        return func(**kwargs)

    return wrapper


@click.group()
def cli() -> None:
    """
    Command line interface for TESMART device RT-05
    If none options are defined, it uses config.toml
    """


@cli.command()
@common_params
def ping(**kwargs: dict) -> None:
    """Ping device"""
    client = get_client(kwargs)
    if client:
        client.ping()


@cli.command()
@common_params
def current(**kwargs: dict) -> None:
    """Get current data from device"""
    client = get_client(kwargs)
    if client:
        client.current()


@cli.command()
@common_params
def history(**kwargs: dict) -> None:
    """Get history data from device"""
    client = get_client(kwargs)
    if client:
        client.history()


@cli.command()
@common_params
def server(**kwargs: dict) -> None:
    client = get_client(kwargs)
    if client:
        run_server(client)


if __name__ == '__main__':
    cli()
