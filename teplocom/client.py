from datetime import datetime

import serial

from teplocom import dicts, utils, command
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
        response = self._make_request(command.PING, DEFAULT_TIMEOUT)
        return response

    def current(self):
        self._dispose()
        response = self._make_request(command.CURRENT, DEFAULT_TIMEOUT)
        response = response.split(' ')
        result = dict()
        for key, value in dicts.current.items():
            if value['type'] == int:
                addr = int(value['addr'], 16)
                result[key] = int(response[addr], 10) if value['size'] == 1 else int(utils.prep_bytes(response[addr:addr + value['size']]), 16)
        self.logger.info(result)
        return result

    def history(self):
        self._dispose()
        response = self._make_request(command.HISTORY, DEFAULT_TIMEOUT)
        pass

    def _make_request(self, command, timeout):
        response = None
        repeat = True
        iteration = 1
        while repeat:
            self._dispose()
            packet = self._init_request()
            packet.extend(bytearray.fromhex(command))
            packet.extend(utils.calc_checksum(packet))
            self.logger.info(utils.format_bytestring(packet))
            self.logger.info(self.client.write(packet))
            response = self._wait_response(timeout)
            if response or iteration == 5:
                repeat = False
            else:
                iteration += 1
        return response

    def _wait_response(self, timeout=10):
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
            length = result[5]
            response = result[6:-1]
            if response.__len__() == length:
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
        packet.extend(bytes([self.slave_id, 0xFF - self.slave_id]))
        return packet

    def _dispose(self):
        self.client.close()
        self.client.open()
