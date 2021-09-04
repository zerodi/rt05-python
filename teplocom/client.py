from datetime import datetime

import serial

from teplocom import dicts, utils, command_code
from teplocom.utils import DEFAULT_TIMEOUT

START_BYTE = bytes.fromhex('55')


class TeplocomClient(object):
    def __init__(self, config, slave_id):
        self.slave_id = slave_id
        self.logger = utils.create_logger()
        self.client = serial.Serial(
            port=config['port'],
            baudrate=int(config['baudrate']),
            parity=config['parity'],
            bytesize=int(config['bytesize']),
            stopbits=int(config['stopbits']),
            rtscts=True,
            dsrdtr=True
        )

    def ping(self):
        self._dispose()
        response = self._make_request(command=command_code.PING, body='', timeout=DEFAULT_TIMEOUT)
        return response

    def current(self):
        self._dispose()
        response = self._make_request(command=command_code.CURRENT, body='00 00 00 00', tlen=1955,
                                      timeout=DEFAULT_TIMEOUT)
        response = response.split(' ')
        result = dict()
        for key, value in dicts.current.items():
            if value['type'] == int:
                addr = int(value['addr'], 16)
                result[key] = int(response[addr], 10) if value['size'] == 1 else int(
                    utils.prep_bytes(response[addr:addr + value['size']]), 16)
        self.logger.info(result)
        return result

    # TODO: Method in progress
    def history(self):
        self._dispose()
        response = self._make_request(command=command_code.HISTORY, body='00 00 00 00 00 00 80 00',
                                      timeout=DEFAULT_TIMEOUT)
        pass

    def _make_request(self, command: tuple, body: str, timeout: int, tlen: int = 0):
        response = None
        repeat = True
        iteration = 1
        while repeat:
            self._dispose()
            packet = self._init_request()
            packet.extend(bytes(command))
            if command == command_code.PING:
                packet.extend(b'\x00')
            elif command == command_code.CURRENT:
                packet_body = bytearray.fromhex(body)
                packet_body.extend(utils.int_to_bytes(tlen))
                packet_body_len = utils.int_to_bytes(len(packet_body))
                packet.extend(packet_body_len)
                packet.extend(packet_body)
            packet.extend(utils.calc_checksum(packet))
            self.logger.info(utils.format_bytestring(packet))
            self.logger.info(self.client.write(packet))
            response = self._wait_response(timeout=timeout, tlen=utils.int_to_bytes(tlen))
            if response or iteration == 5:
                repeat = False
            else:
                iteration += 1
        return response

    def _wait_response(self, tlen: bytes, timeout: int = 10):
        result = bytearray()
        start_time = datetime.now()
        while True:
            time_delta = datetime.now() - start_time
            bytes_to_read = self.client.inWaiting()
            if bytes_to_read:
                self.logger.info(bytes_to_read)
                byte_str = self.client.read(bytes_to_read)
                self.logger.info(utils.format_bytestring(byte_str))
                result.extend(byte_str)
            if time_delta.total_seconds() >= timeout:
                break
        self.client.close()
        self.logger.info(result)
        if self._validate_response(result):
            start = 5
            tlen_bytes_len = len(tlen)
            if tlen:
                length = int.from_bytes(result[start:start + tlen_bytes_len], byteorder='big')
                response = result[start + tlen_bytes_len:-1]
            else:
                length = int.from_bytes(result[start:start+1], byteorder='big')
                response = result[start + 1:-1]
            if len(response) == length:
                response = utils.format_bytestring(response)
                self.logger.info(response)
                return response
            else:
                self.logger.error('Invalid Response Length')
                return False
        else:
            self.logger.error('Invalid Checksum')
            return False

    def _validate_response(self, response):
        _response = response[:-1]
        _checksum = response[-1:]
        return utils.calc_checksum(_response) == _checksum

    def _init_request(self):
        packet = bytearray()
        packet.extend(START_BYTE)
        packet.extend(utils.slave_bytes(self.slave_id))
        return packet

    def _dispose(self):
        self.client.close()
        self.client.open()
