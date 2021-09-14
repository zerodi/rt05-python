from datetime import datetime
from typing import Optional

import serial

from tesmart import command_code, dicts, utils
from tesmart.utils import DEFAULT_TIMEOUT, try_repeat

START_BYTE = bytes.fromhex('55')


class TesmartClient:
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
        response = self._make_request(command=command_code.CURRENT, body='00 00 00 00 07 A3', timeout=DEFAULT_TIMEOUT)
        result = dicts.transform_current_response(response)
        self.logger.info(result)
        return result

    def history(self) -> None:
        self._dispose()
        self._make_request(command=command_code.HISTORY, body='00 00 00 00 00 00 80 00', timeout=DEFAULT_TIMEOUT)
        return None

    @try_repeat(times=5)
    def _make_request(self, command: tuple, body: str, timeout: int) -> Optional[bytearray]:
        self._dispose()
        packet = self._build_request_body(command, body)
        self.logger.info(self.client.write(packet))
        return self._wait_response(timeout=timeout)

    def _wait_response(self, timeout: int = 10) -> Optional[bytearray]:
        result: bytearray = self._read_bytes(timeout)
        self.client.close()
        self.logger.info(result)
        if utils.validate_response(result):
            length, response = self._read_response(result)
            self.logger.info(response)
            self.logger.info(utils.format_bytestring(response))
            return response
        else:
            self.logger.error('Invalid Checksum')
            return None

    def _build_request_body(self, command: tuple, body: str) -> bytearray:
        packet = self._init_request()
        packet.extend(bytes(command))
        if command == command_code.PING:
            self._build_ping_request(packet)
        elif command == command_code.CURRENT:
            self._build_current_request(packet, body)
        elif command == command_code.HISTORY:
            self._build_current_request(packet, body)
        packet.extend(utils.calc_checksum(packet))
        self.logger.info(utils.format_bytestring(packet))
        return packet

    def _build_ping_request(self, packet: bytearray) -> None:
        packet.extend(b'\x00')

    def _build_current_request(self, packet: bytearray, body: str) -> None:
        packet_body = bytearray.fromhex(body)
        packet_body_len = utils.int_to_bytes(len(packet_body))
        packet.extend(packet_body_len)
        packet.extend(packet_body)

    def _build_history_request(self, packet: bytearray, body: str) -> None:
        packet_body = bytearray.fromhex(body)
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

    def _read_response(self, result: bytearray) -> tuple[int, bytearray]:
        start = 5
        length = utils.bytes_to_int(result[start : start + 1])
        response = result[start + 1 : -1]
        return length, response

    def _init_request(self) -> bytearray:
        packet = bytearray()
        packet.extend(START_BYTE)
        packet.extend(utils.slave_bytes(self.slave_id))
        return packet

    def _dispose(self) -> None:
        self.client.close()
        self.client.open()
