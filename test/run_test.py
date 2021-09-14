from test.device import run_mock_device
from test.emulator import SerialEmulator

if __name__ == '__main__':
    emulator = SerialEmulator()
    try:
        print('device_port:', emulator.device_port)
        print('client_port:', emulator.client_port)
        run_mock_device(emulator.device_port)
    except KeyboardInterrupt:
        pass
    emulator.stop()
