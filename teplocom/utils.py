import codecs
import logging

DEFAULT_TIMEOUT = 10


def prep_bytes(byte_str):
    byte_str.reverse()
    return ''.join(byte_str)


def calc_checksum(packet):
    return bytes([(~sum(packet) & 0xFF)])


def format_bytestring(resp):
    response = _decode(resp)
    return '%s' % (_format_data(response.upper()))


def int_to_bytes(val: int) -> bytes:
    return val.to_bytes((val.bit_length() + 7) // 8, byteorder='big')


def slave_bytes(slave_id: int) -> bytes:
    return bytes([slave_id, 0xFF - slave_id])


def _decode(resp):
    return str(codecs.encode(resp, 'hex').decode('ascii'))


def _format_data(data):
    fmt_data = ''
    for i in range(0, len(data), 2):
        fmt_data += (data[i:i+2] + ' ')
    return fmt_data


class ConsoleHandler(logging.Handler):
    """This class is a logger handler. It prints on the console"""

    def __init__(self):
        """Constructor"""
        logging.Handler.__init__(self)

    def emit(self, record):
        """format and print the record on the console"""
        print(self.format(record))


def create_logger(level=logging.DEBUG, record_format=None):
    """Create a logger according to the given settings"""
    if record_format is None:
        record_format = "%(asctime)s\t%(levelname)s\t%(module)s.%(funcName)s\t%(threadName)s\t%(message)s"

    logger = logging.getLogger("teplocom")
    logger.setLevel(level)
    formatter = logging.Formatter(record_format)
    log_handler = ConsoleHandler()
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
    return logger