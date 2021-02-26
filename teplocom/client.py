from datetime import datetime

import modbus_tk.utils
import serial

import dicts
import utils

START_BYTE = bytes.fromhex('55')


class TeplocomClient(object):
    def __init__(self, config, slave_id):
        self.port = config['port']
        self.slave_id = slave_id
        self.logger = modbus_tk.utils.create_logger("console")
        self.client = serial.Serial(
            port=self.port,
            baudrate=int(config['baudrate']),
            parity=config['parity'],
            bytesize=int(config['bytesize']),
            stopbits=int(config['stopbits']),
            rtscts=True,
            dsrdtr=True
        )

    def ping(self):
        command = '00 00 00'
        self._dispose()
        response = self._make_request(command)
        return response

    """
    Current - 0F 01 06 00 00 00 00 07 A3
    """

    def current(self):
        command = '0F 01 06 00 00 00 00 07 A3'
        self._dispose()
        response = self._make_request(command)
        result = dict()
        for key, value in dicts.current.items():
            if value['type'] == int:
                addr = int(value['addr'], 16)
                if value['size'] == 1:
                    result[key] = int(response[addr], 16)
                else:
                    result[key] = int(utils.prep_bytes(response[addr:addr + value['size']]), 16)
        self.logger.info(result)
        return result

    """
    History - 0F 03 08 00 00 00 00 00 00 80 00
    """

    def history(self):
        pass

    def _make_request(self, command):
        response = None
        repeat = True
        iteration = 1
        while repeat:
            self._dispose()
            packet = self._init_request()
            packet.extend(bytearray.fromhex(command))
            packet.extend(utils.calc_checksum(packet))
            self.logger.info(packet)
            self.logger.info(self.client.write(packet))
            response = self._wait_response()
            if response or iteration == 5:
                repeat = False
            else:
                iteration += 1
        return response

    def _wait_response(self):
        result = bytearray()
        start_time = datetime.now()
        while True:
            time_delta = datetime.now() - start_time
            bytesToRead = self.client.inWaiting()
            if bytesToRead:
                self.logger.info(bytesToRead)
                result.extend(self.client.read(bytesToRead))
            if time_delta.total_seconds() >= 20:
                break
        self.client.close()
        self.logger.info(result)
        if self._validate_response(result):
            length = result[5]
            response = result[6:-1]
            if True:  # response.__len__() == length:
                response = utils.prepare_response(response)
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
