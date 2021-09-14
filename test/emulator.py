import subprocess
import time


class SerialEmulator:
    def __init__(self, device_port: str = './ttydevice', client_port: str = './ttyclient') -> None:
        self.device_port = device_port
        self.client_port = client_port
        cmd = ['socat', '-d', '-d', f'PTY,link={self.device_port},raw,echo=0', f'PTY,link={self.client_port},raw,echo=0']
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1)
        self.err: bytes
        self.out: bytes

    def __del__(self) -> None:
        self.stop()

    def stop(self) -> None:
        self.proc.kill()
        self.out, self.err = self.proc.communicate()

    @staticmethod
    def start(device_port: str = './ttydevice', client_port: str = './ttyclient') -> tuple[str, str]:
        emulator = SerialEmulator(device_port, client_port)
        return emulator.device_port, emulator.client_port
