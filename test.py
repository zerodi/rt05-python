import socket
import sys
from teplocom import utils
from datetime import datetime
import struct
#req = '55 02 FD 0F 01 06 00 00 00 00 07 A3'
req = '55 02 FD 0F 03 08 00 00 00 00 00 00 80 00'
# req = '55 02 FD 00 00 00'

HOST, PORT = '127.0.0.1', 50001

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    packet = bytearray.fromhex(req)
    packet.extend(utils.calc_checksum(packet))
    sock.sendall(packet)
    print("Sent:     {}".format(utils.format_bytestring(packet)))
    start_time = datetime.now()
    repeat = True
    result = bytearray()
    sock.settimeout(10.0)
    try:
        while True:
            received = sock.recv(1024)
            print("Received: {}".format(utils.format_bytestring(received)))
            if received:
                result.extend(received)
    except socket.timeout:
        print("Result: {}".format(utils.format_bytestring(result)))
        _response = result[:-1]
        _checksum = result[-1:]
        print("Response Size: {}".format(len(result)))
        print("Checksum Valid: {}".format(utils.calc_checksum(_response) == _checksum))
    finally:
        sock.close()
    # received = sock.recv(6)
    # print("Received: {}".format(utils.format_bytestring(received)))
    # byte_size = struct.unpack('<BBBBBB', received)[5]
    # print("Bytes: {}".format(byte_size))
    # received += sock.recv(byte_size+1)







# class Client(object):
#
#     def __init__(self):
#         self.buffer = ''
#         self.sock = None
#
#     def connect(self,address):
#         self.buffer = ''
#         self.sock = socket.socket()
#         self.sock.connect(address)
#
#     def send(self):
#         packet = bytearray.fromhex(req)
#         packet.extend(utils.calc_checksum(packet))
#         self.sock.sendall(packet)
#
#     def get_msg(self):
#         '''Append raw data to buffer until sentinel is found,
#            then strip off the message, leaving the remainder
#            in the buffer.
#         '''
#         while not '\n' in self.buffer:
#             data = self.sock.recv(4096)
#             print(data)
#             if not data:
#                 return ''
#             self.buffer += data
#         sentinel = self.buffer.index('\n') + 1
#         msg,self.buffer = self.buffer[:sentinel],self.buffer[sentinel:]
#         return msg
#
#     def close(self):
#         self.sock.close()
#
#
# if __name__ == '__main__':
#     c = Client()
#     c.connect((HOST,PORT))
#     c.send()
#     while True:
#         msg = c.get_msg()
#         if not msg:
#             break
#         print(repr(msg))
#     c.close()