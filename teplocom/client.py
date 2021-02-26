import serial
import modbus_tk.utils
import os
from datetime import datetime

START_BYTE = bytes.fromhex('55')

"""
for codec in codec_names.keys():
    try:
        print(res.decode(codec))
    except:
        pass
"""

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
        self._dispose()
        packet = self._init_request()
        packet.extend(bytearray.fromhex('00 00 00'))
        packet.extend(self._calc_checksum(packet))
        self.logger.info(packet)
        self.logger.info(self.client.write(packet))
        self._wait_response()

    def current(self):
        repeat = True
        iteration = 1
        while repeat:
            self._dispose()
            packet = self._init_request()
            """
            Current - 0F 01 06 00 00 00 00 07 A3
            History - 0F 03 08 00 00 00 00 00 00 80 00
            """
            packet.extend(bytearray.fromhex('0F 03 08 00 00 00 00 00 00 80 00'))
            packet.extend(self._calc_checksum(packet))
            self.logger.info(packet)
            self.logger.info(self.client.write(packet))
            success = self._wait_response()
            if success or iteration == 5:
                repeat = False
            else:
                iteration += 1


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
            self.logger.info(response)
            # if response.__len__() == length:
            #     self.logger.info(response)
            # else:
            #     self.logger.error('Invalid Response Length')
            return True
        else:
            self.logger.error('Invalid Checksum')
            return False

    def _validate_response(self, response):
        _response = response[:-1]
        _checksum = response[-1:]
        return self._calc_checksum(_response) == _checksum

    def _init_request(self):
        packet = bytearray()
        packet.extend(START_BYTE)
        packet.extend(bytes([self.slave_id, 0xFF - self.slave_id]))
        return packet

    def _dispose(self):
        self.client.close()
        self.client.open()

    def _calc_checksum(self, packet):
        return bytes([(~sum(packet) & 0xFF)])

    def connect(self):
        self._dispose()
        packet = bytearray()
        packet.extend(START_BYTE)
        packet.extend(bytes([self.slave_id, 0xFF - self.slave_id]))
        packet.extend(bytearray.fromhex('00 00 00'))
        crc = bytes([(~sum(packet) & 0xFF)])
        packet.extend(crc)
        self.logger.info(packet)
        """'5502FD0F01060000000007A3EB'"""
        # packet = bytearray.fromhex('55 02 F 00 00 00 AB')
        self.logger.info(self.client.write(packet))
        result = bytearray()
        start_time = datetime.now()
        while True:
            time_delta = datetime.now() - start_time
            bytesToRead = self.client.inWaiting()
            if (bytesToRead):
                self.logger.info(bytesToRead)
                result.extend(self.client.read(bytesToRead))
            if time_delta.total_seconds() >= 10:
                break
        self.client.close()
        self.logger.info(result)
        self.logger.info(result.decode('cp866'))
