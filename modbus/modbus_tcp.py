import serial
import datetime
import modbus_tk.utils
from modbus_tk.modbus_rtu_over_tcp import RtuOverTcpMaster
from modbus_tk import hooks
from modbus_tk.modbus import ModbusError
import modbus_tk.defines as cst


class ModbusTcp(object):
    def __init__(self, config):
        self.logger = modbus_tk.utils.create_logger("console")

        def on_after_recv(data):
            master, bytes_data = data
            self.logger.info(bytes_data)

        def on_before_connect(args):
            master = args[0]
            self.logger.debug("on_before_connect {0} {1}".format(master._host, master._port))

        def on_after_recv(args):
            response = args[1]
            self.logger.debug("on_after_recv {0} bytes received".format(len(response)))

        hooks.install_hook('modbus.Master.after_recv', on_after_recv)
        hooks.install_hook("modbus_tcp.TcpMaster.before_connect", on_before_connect)
        hooks.install_hook("modbus_tcp.TcpMaster.after_recv", on_after_recv)

        self.slave_id = 2
        try:
            self.server = RtuOverTcpMaster(
                host='127.0.0.1',
                port=50001
            )
            self.server.open()

            self.server.set_timeout(5.0)
            self.server.set_verbose(True)
        except ModbusError as exc:
            self.logger.error("%s- Code=%d", exc, exc.get_exception_code())

    def connect(self):
        """"""
        result = self.server.execute(self.slave_id, cst.READ_COILS, 0, 0)
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