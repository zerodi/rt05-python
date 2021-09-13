import functools
import os
import sys
from typing import Callable, Optional

import click
import toml

from tesmart.client import TesmartClient


def read_config_from_file(opts: dict) -> tuple[dict, int]:
    try:
        config = toml.load(os.path.abspath(opts['config'] or 'config.toml'))
        connect_config = config['SERIAL']
        slave_id = config['DEVICE']['slave_id']
        return connect_config, slave_id
    except FileNotFoundError:
        print('Specify port or create config.toml file.')
        sys.exit(1)


def read_config_from_opts(opts: dict) -> tuple[dict, int]:
    connect_config = dict(
        port=opts['port'],
        baudrate=opts['baudrate'],
        parity=opts['parity'],
        bytesize=opts['bytesize'],
        stopbits=opts['stopbits'],
    )
    slave_id = opts['slave_id']
    return connect_config, slave_id


def get_client(opts: dict) -> Optional[TesmartClient]:
    if opts['port'] is None:
        connect_config, slave_id = read_config_from_file(opts)
    else:
        connect_config, slave_id = read_config_from_opts(opts)
    return TesmartClient(connect_config, slave_id)


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


if __name__ == '__main__':
    cli()
