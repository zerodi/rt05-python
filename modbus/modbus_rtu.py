import serial
import datetime
import modbus_tk.utils
from modbus_tk.modbus_rtu import RtuMaster
from modbus_tk.modbus import ModbusError
import modbus_tk.defines as cst


class ModbusRtu(object):
    def __init__(self, rtu_config):
        self.logger = modbus_tk.utils.create_logger("console")
        self.slave_id = 2
        try:
            self.server = RtuMaster(serial.Serial(
                port=rtu_config['port'],
                baudrate=int(rtu_config['baudrate']),
                parity=rtu_config['parity'],
                bytesize=int(rtu_config['bytesize']),
                stopbits=int(rtu_config['stopbits']),
            ))
            self.server.open()

            self.server.set_timeout(5.0)
            self.server.set_verbose(True)
        except ModbusError as exc:
            self.logger.error("%s- Code=%d", exc, exc.get_exception_code())

    def connect(self):
        """"""
        result = self.server.execute(self.slave_id, cst.READ_INPUT_REGISTERS, 0, 0)
        self.logger(result)

    def get_time(self):
        I_STARTING_REGISTER = 1024
        I_REGISTERS_TO_READ = 6
        try:
            result = self.server.execute(self.slave_id, cst.READ_INPUT_REGISTERS, I_STARTING_REGISTER, I_REGISTERS_TO_READ)
            date = datetime.datetime(
                year=2000 + result[5],
                month=result[4],
                day=result[3],
                hour=result[2],
                minute=result[1],
                second=result[0]
            )
            self.logger.info(date)

        except ModbusError as exc:
            self.logger.error("%s- Code=%d", exc, exc.get_exception_code())