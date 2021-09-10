import codecs
import functools
import logging
from typing import Any, Callable, Optional

DEFAULT_TIMEOUT = 10


def try_repeat(times: int = 5) -> Callable:
    def real_repeat(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper_repeat(*args: Any, **kwargs: Any) -> Optional[Any]:
            repeat = True
            iteration = 1
            result = None
            while repeat:
                result = func(*args, **kwargs)
                if result or iteration == times:
                    repeat = False
                else:
                    iteration += 1
            return result

        return wrapper_repeat

    return real_repeat


def prep_bytes(byte_str: list[str]) -> str:
    byte_str.reverse()
    return ''.join(byte_str)


def calc_checksum(packet: bytearray) -> bytes:
    return bytes([(~sum(packet) & 0xFF)])


def format_bytestring(response: bytearray) -> str:
    response_str: str = _decode(response)
    return f'{_format_data(response_str.upper())}'


def int_to_bytes(value: int) -> bytes:
    return value.to_bytes((value.bit_length() + 7) // 8, byteorder='big')


def slave_bytes(slave_id: int) -> bytes:
    return bytes([slave_id, 0xFF - slave_id])


def _decode(response: bytearray) -> str:
    return str(codecs.encode(response, 'hex').decode('ascii'))


def _format_data(data: str) -> str:
    fmt_data = ''
    for i in range(0, len(data), 2):
        fmt_data += data[i : i + 2] + ' '
    return fmt_data


class ConsoleHandler(logging.Handler):
    def __init__(self) -> None:
        logging.Handler.__init__(self)

    def emit(self, record: logging.LogRecord) -> None:
        print(self.format(record))


def create_logger(level: int = logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger('teplocom')
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(module)s.%(funcName)s\t%(threadName)s\t%(message)s')
    log_handler = ConsoleHandler()
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
    return logger
