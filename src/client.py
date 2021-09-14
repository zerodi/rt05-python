import os
import sys
from typing import Optional

import toml

from tesmart.client import TesmartClient


def read_config_from_file(opts: dict) -> tuple[dict, int]:
    config = toml.load(os.path.abspath(opts['config'] or 'config.toml'))
    connect_config = config['SERIAL']
    slave_id = config['DEVICE']['slave_id']
    return connect_config, slave_id


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
    try:
        if opts['port'] is None:
            connect_config, slave_id = read_config_from_file(opts)
        else:
            connect_config, slave_id = read_config_from_opts(opts)
        return TesmartClient(connect_config, slave_id)
    except FileNotFoundError:
        print('Specify port or create config.toml file.')
        sys.exit(1)
    return None
