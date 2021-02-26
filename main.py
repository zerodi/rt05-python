# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import configparser
import datetime

from modbus.modbus_rtu import ModbusRtu
from modbus.modbus_tcp import ModbusTcp
from teplocom.client import TeplocomClient
SLAVE_ID = 2

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    rtu_config = config['SERIAL']

    # server = ModbusRtu(rtu_config)
    # server = ModbusTcp(rtu_config)
    # server.get_time()
    # server.connect()
    client = TeplocomClient(rtu_config, SLAVE_ID)
    client.current()
