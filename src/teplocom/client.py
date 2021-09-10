from datetime import datetime
from typing import Optional

import serial

from teplocom import command_code, dicts, utils
from teplocom.utils import DEFAULT_TIMEOUT, try_repeat

START_BYTE = bytes.fromhex('55')


class TeplocomClient:
    def __init__(self, config: dict, slave_id: int):
        self.slave_id = slave_id
        self.logger = utils.create_logger()
        self.client = serial.Serial(
            port=config['port'],
            baudrate=int(config['baudrate']),
            parity=config['parity'],
            bytesize=int(config['bytesize']),
            stopbits=int(config['stopbits']),
            rtscts=True,
            dsrdtr=True,
        )

    def ping(self) -> bytearray:
        self._dispose()
        return self._make_request(command=command_code.PING, body='', timeout=DEFAULT_TIMEOUT)

    def current(self) -> dict:
        self._dispose()
        response = self._make_request(command=command_code.CURRENT, body='00 00 00 00', tlen=1955, timeout=DEFAULT_TIMEOUT)
        result = dicts.transform_current_response(response)
        self.logger.info(result)
        return result

    """
    TODO: This method in progress
    """

    def history(self) -> None:
        self._dispose()
        self._make_request(command=command_code.HISTORY, body='00 00 00 00 00 00 80 00', timeout=DEFAULT_TIMEOUT)
        return None

    @try_repeat(times=5)
    def _make_request(self, command: tuple, body: str, timeout: int, tlen: int = 0) -> Optional[bytearray]:
        self._dispose()
        packet = self._build_request_body(command, body, tlen)
        self.logger.info(self.client.write(packet))
        return self._wait_response(timeout=timeout, tlen=utils.int_to_bytes(tlen))

    def _wait_response(self, tlen: bytes, timeout: int = 10) -> Optional[bytearray]:
        result: bytearray = self._read_bytes(timeout)
        self.client.close()
        self.logger.info(result)
        if self._validate_response(result):
            length, response = self._read_response(result, tlen)
            if len(response) == length:
                self.logger.info(response)
                self.logger.info(utils.format_bytestring(response))
                return response
            else:
                self.logger.error('Invalid Response Length')
                return None
        else:
            self.logger.error('Invalid Checksum')
            return None

    def _build_request_body(self, command: tuple, body: str, tlen: int) -> bytearray:
        packet = self._init_request()
        packet.extend(bytes(command))
        if command == command_code.PING:
            self._build_ping_request(packet)
        elif command == command_code.CURRENT:
            self._build_current_request(packet, body, tlen)
        packet.extend(utils.calc_checksum(packet))
        self.logger.info(utils.format_bytestring(packet))
        return packet

    def _build_ping_request(self, packet: bytearray) -> None:
        packet.extend(b'\x00')

    def _build_current_request(self, packet: bytearray, body: str, tlen: int) -> None:
        packet_body = bytearray.fromhex(body)
        packet_body.extend(utils.int_to_bytes(tlen))
        packet_body_len = utils.int_to_bytes(len(packet_body))
        packet.extend(packet_body_len)
        packet.extend(packet_body)

    def _read_bytes(self, timeout: int = 10) -> bytearray:
        result = bytearray()
        start_time = datetime.now()
        while True:
            time_delta = datetime.now() - start_time
            bytes_to_read = self.client.inWaiting()
            if bytes_to_read:
                self.logger.info(bytes_to_read)
                byte_str = self.client.read(bytes_to_read)
                self.logger.info(utils.format_bytestring(bytearray(byte_str)))
                result.extend(byte_str)
            if time_delta.total_seconds() >= timeout:
                break
        return result

    def _read_response(self, result: bytearray, tlen: bytes) -> tuple[int, bytearray]:
        start = 5
        tlen_bytes_len = len(tlen)
        if tlen:
            length = int.from_bytes(result[start : start + tlen_bytes_len], byteorder='big')
            response = result[start + tlen_bytes_len : -1]
        else:
            length = int.from_bytes(result[start : start + 1], byteorder='big')
            response = result[start + 1 : -1]
        return length, response

    def _validate_response(self, response: bytearray) -> bool:
        _response = response[:-1]
        _checksum = response[-1:]
        return utils.calc_checksum(_response) == _checksum

    def _init_request(self) -> bytearray:
        packet = bytearray()
        packet.extend(START_BYTE)
        packet.extend(utils.slave_bytes(self.slave_id))
        return packet

    def _dispose(self) -> None:
        self.client.close()
        self.client.open()
